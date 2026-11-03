// Research only: models the input/output buffer costs around CatServer's compressor.
// This is NOT Netty, does not include packet framing, and never runs in server.jar.
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.zip.Deflater;

public final class PacketPipelineBench {
    private static final int MAX_PACKET = 1024 * 1024;
    private static volatile int consumed;

    private static int javaEncode(Deflater deflater, ByteBuffer source, ByteBuffer result,
                                  byte[] scratch) {
        // CatServer copies the readable packet into a new byte[] before Deflater.setInput.
        byte[] payload = new byte[source.remaining()];
        source.duplicate().get(payload);
        deflater.setInput(payload);
        deflater.finish();
        int total = 0;
        try {
            while (!deflater.finished()) {
                int n = deflater.deflate(scratch);
                if (n < 1 || n > result.remaining())
                    throw new IllegalStateException("Java output buffer exhausted");
                result.put(scratch, 0, n);
                total += n;
            }
            return total;
        } finally {
            deflater.reset();
        }
    }

    private static int nativeEncode(long handle, ByteBuffer source, ByteBuffer result) {
        // Direct input may be used in-place; heap input requires a direct staging copy.
        ByteBuffer input = source;
        if (!source.isDirect()) {
            input = ByteBuffer.allocateDirect(source.remaining());
            input.put(source.duplicate()).flip();
        }
        int written = NativeDeflater.compress(handle, input, source.remaining(), result);
        if (written < 1 || written > result.capacity())
            throw new IllegalStateException("native compression failed");
        result.position(written);
        return written;
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 5)
            throw new IllegalArgumentException("INPUT NEW_OUTPUT LOOPS heap|direct java|native");
        Path destination = Path.of(args[1]);
        int loops = Integer.parseInt(args[2]);
        if (Files.exists(destination) || loops < 1 || loops > 5000 ||
                !(args[3].equals("heap") || args[3].equals("direct")) ||
                !(args[4].equals("java") || args[4].equals("native")))
            throw new IllegalArgumentException("invalid benchmark arguments");
        byte[] bytes = Files.readAllBytes(Path.of(args[0]));
        if (bytes.length < 1 || bytes.length > MAX_PACKET)
            throw new IllegalArgumentException("invalid public packet size");
        ByteBuffer source = args[3].equals("direct") ? ByteBuffer.allocateDirect(bytes.length)
                                                        : ByteBuffer.allocate(bytes.length);
        source.put(bytes).flip();
        boolean nativeArm = args[4].equals("native");
        Deflater deflater = nativeArm ? null : new Deflater(6);
        long handle = nativeArm ? NativeDeflater.create(6) : 0;
        if (nativeArm && handle == 0) throw new IllegalStateException("native unavailable");
        byte[] scratch = new byte[8192];
        try {
            long start = 0;
            ByteBuffer lastResult = null;
            int lastWritten = 0;
            for (int i = -20; i < loops; i++) {
                // Netty supplies a fresh output buffer for each packet. In this controlled
                // model it is a contiguous direct buffer with enough capacity for zlib.
                ByteBuffer result = ByteBuffer.allocateDirect(bytes.length + 1024);
                int written = nativeArm ? nativeEncode(handle, source, result)
                                        : javaEncode(deflater, source, result, scratch);
                consumed ^= result.get(0) ^ result.get(written - 1);
                if (i == -1) start = System.nanoTime();
                if (i == loops - 1) {
                    lastResult = result;
                    lastWritten = written;
                }
            }
            double millis = (System.nanoTime() - start) / 1_000_000.0;
            byte[] compressed = new byte[lastWritten];
            lastResult.flip();
            lastResult.get(compressed);
            Files.write(destination, compressed);
            System.out.printf("PIPELINE_MS=%.3f arm=%s source=%s loops=%d bytes=%d sink=%d%n",
                    millis, args[4], args[3], loops, bytes.length, consumed);
        } finally {
            if (deflater != null) deflater.end();
            if (handle != 0) NativeDeflater.destroy(handle);
        }
    }
}
