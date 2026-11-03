// Public research contract only. This models CatServer's threshold/VarInt/zlib
// framing but does NOT extract its Netty encoder or run the RP pack.
import java.io.ByteArrayOutputStream;
import java.io.BufferedReader;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Random;
import java.util.Set;
import java.util.zip.DataFormatException;
import java.util.zip.Deflater;
import java.util.zip.Inflater;

public final class PacketDifferential281 {
    private static final int MAX = 2097152;

    private static byte[] payload(int size, String pattern, int seed) {
        if (size < 0 || size > MAX) throw new IllegalArgumentException("public packet outside protocol limit");
        byte[] data = new byte[size];
        switch (pattern) {
            case "zeros": return data;
            case "repeat":
                for (int i = 0; i < size; i++) data[i] = (byte)(i % 4 + 65);
                return data;
            case "random": new Random(0xFC1165L + seed).nextBytes(data); return data;
            case "mixed":
                byte[] random = new byte[size - size / 2];
                new Random(0xFC1165L + seed).nextBytes(random);
                System.arraycopy(random, 0, data, size / 2, random.length);
                return data;
            default: throw new IllegalArgumentException("unknown public pattern");
        }
    }

    private static void varInt(ByteArrayOutputStream out, int value) {
        do {
            int next = value & 127;
            value >>>= 7;
            out.write(value == 0 ? next : next | 128);
        } while (value != 0);
    }

    private static byte[] encode(byte[] raw, int threshold, boolean nativeArm,
                                 boolean direct, Deflater deflater, long nativeHandle) {
        if (threshold < 0 || threshold > MAX) throw new IllegalArgumentException("invalid threshold");
        ByteArrayOutputStream frame = new ByteArrayOutputStream();
        if (raw.length < threshold) {
            varInt(frame, 0);
            frame.write(raw, 0, raw.length);
            return frame.toByteArray();
        }
        varInt(frame, raw.length);
        if (!nativeArm) {
            byte[] copy = raw.clone(); // CatServer reads a fresh byte[] from ByteBuf.
            byte[] scratch = new byte[8192];
            deflater.setInput(copy);
            deflater.finish();
            try {
                while (!deflater.finished()) {
                    int n = deflater.deflate(scratch);
                    if (n < 1) throw new IllegalStateException("Java zlib stalled");
                    frame.write(scratch, 0, n);
                }
            } finally {
                deflater.reset();
            }
        } else {
            ByteBuffer input = direct ? ByteBuffer.allocateDirect(raw.length)
                                      : ByteBuffer.wrap(raw);
            if (direct) input.put(raw).flip();
            if (!direct) {
                ByteBuffer staging = ByteBuffer.allocateDirect(raw.length);
                staging.put(input.duplicate()).flip();
                input = staging;
            }
            ByteBuffer output = ByteBuffer.allocateDirect(raw.length + 1024);
            int n = NativeDeflater.compress(nativeHandle, input, raw.length, output);
            if (n <= 0 || n > output.capacity())
                throw new IllegalStateException("JNI zlib unavailable or buffer too small");
            byte[] stream = new byte[n];
            output.get(stream);
            frame.write(stream, 0, stream.length);
        }
        return frame.toByteArray();
    }

    private static byte[] strictDecode(byte[] frame, int threshold) throws DataFormatException {
        int position = 0;
        int declared = 0;
        boolean done = false;
        for (int i = 0; i < 5; i++) {
            if (position == frame.length) throw new DataFormatException("short VarInt");
            int octet = frame[position++] & 255;
            if (i == 4 && octet > 7) throw new DataFormatException("VarInt overflow");
            declared |= (octet & 127) << (7 * i);
            if ((octet & 128) == 0) { done = true; break; }
        }
        if (!done || declared < 0 || declared > MAX) throw new DataFormatException("invalid length");
        if (declared == 0) {
            byte[] result = Arrays.copyOfRange(frame, position, frame.length);
            if (result.length >= threshold || result.length > MAX)
                throw new DataFormatException("uncompressed threshold mismatch");
            return result;
        }
        if (declared < threshold) throw new DataFormatException("compressed threshold mismatch");
        Inflater inflater = new Inflater();
        try {
            inflater.setInput(frame, position, frame.length - position);
            ByteArrayOutputStream out = new ByteArrayOutputStream(Math.min(declared, 8192));
            byte[] scratch = new byte[8192];
            while (!inflater.finished()) {
                int n = inflater.inflate(scratch);
                if (n == 0) throw new DataFormatException("truncated or stalled zlib");
                out.write(scratch, 0, n);
                if (out.size() > declared) throw new DataFormatException("inflated beyond declared size");
            }
            if (inflater.getRemaining() != 0 || out.size() != declared)
                throw new DataFormatException("trailing zlib data or length mismatch");
            return out.toByteArray();
        } finally {
            inflater.end();
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("PUBLIC_MANIFEST_PATH");
        long handle = NativeDeflater.create(6);
        if (handle == 0) throw new IllegalStateException("no native compressor");
        Deflater deflater = new Deflater(6);
        Set<String> identities = new HashSet<>();
        int cases = 0;
        byte[] mutant = null;
        try (BufferedReader reader = Files.newBufferedReader(Path.of(args[0]))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] fields = line.split("\\t", -1);
                if (fields.length != 5 || !fields[0].equals(String.format("PKT-%03d", cases)) ||
                        !identities.add(line)) throw new IllegalArgumentException("manifest drift");
                int size = Integer.parseInt(fields[1]);
                int threshold = Integer.parseInt(fields[4]);
                boolean direct;
                if (fields[3].equals("direct")) direct = true;
                else if (fields[3].equals("heap")) direct = false;
                else throw new IllegalArgumentException("invalid source representation");
                byte[] raw = payload(size, fields[2], cases);
                byte[] javaFrame = encode(raw, threshold, false, direct, deflater, handle);
                byte[] nativeFrame = encode(raw, threshold, true, direct, deflater, handle);
                if (!Arrays.equals(strictDecode(javaFrame, threshold), raw) ||
                        !Arrays.equals(strictDecode(nativeFrame, threshold), raw))
                    throw new AssertionError("differential payload mismatch: " + fields[0]);
                if (cases == 0) {
                    mutant = nativeFrame.clone();
                    mutant[0] = 1; // Deliberately misdeclare bypass as compressed.
                }
                cases++;
            }
            if (cases != 261) throw new AssertionError("261 distinct packet cases required");
            boolean rejected = false;
            try {
                if (!Arrays.equals(strictDecode(mutant, 256), payload(1, "zeros", 0))) rejected = true;
            } catch (DataFormatException expected) { rejected = true; }
            if (!rejected) throw new AssertionError("corrupt frame not rejected");
            System.out.println("PACKET_DIFFERENTIAL_PASS cases=" + cases + " corrupted_header_rejected=true public_only=true");
        } finally {
            deflater.end();
            NativeDeflater.destroy(handle);
        }
    }
}
