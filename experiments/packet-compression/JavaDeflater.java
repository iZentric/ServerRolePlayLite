// Public packet corpus only; mirrors CatServer's persistent java.util.zip.Deflater.
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.zip.Deflater;

public final class JavaDeflater {
    private static int encode(Deflater compressor, byte[] input, byte[] output) {
        compressor.setInput(input);
        compressor.finish();
        int written = 0;
        while (!compressor.finished()) {
            int n = compressor.deflate(output, written, output.length - written);
            if (n == 0) throw new IllegalStateException("zlib output buffer exhausted");
            written += n;
        }
        compressor.reset();
        return written;
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 3) throw new IllegalArgumentException("INPUT OUTPUT LOOPS");
        Path output = Path.of(args[1]);
        int loops = Integer.parseInt(args[2]);
        if (Files.exists(output) || loops < 1 || loops > 10000)
            throw new IllegalArgumentException("invalid output/loops");
        byte[] input = Files.readAllBytes(Path.of(args[0]));
        if (input.length < 1 || input.length > 1024 * 1024)
            throw new IllegalArgumentException("invalid public packet size");
        byte[] compressed = new byte[input.length + 1024];
        Deflater compressor = new Deflater(6);
        try {
            for (int i = 0; i < 100; i++) encode(compressor, input, compressed);
            long start = System.nanoTime();
            int written = 0;
            for (int i = 0; i < loops; i++) written = encode(compressor, input, compressed);
            double millis = (System.nanoTime() - start) / 1_000_000.0;
            Files.write(output, java.util.Arrays.copyOf(compressed, written));
            System.out.printf("JAVA_ZLIB_MS=%.3f loops=%d source_bytes=%d compressed_bytes=%d%n",
                              millis, loops, input.length, written);
        } finally {
            compressor.end();
        }
    }
}
