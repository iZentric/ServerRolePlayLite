// Research only: direct ByteBuffer -> JNI -> pinned MIT libdeflate. Not in server.jar.
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;

public final class NativeDeflater {
    static { System.loadLibrary("fc_native"); }
    private static native long create(int level);
    private static native int compress(long handle, ByteBuffer input, int length, ByteBuffer output);
    private static native void destroy(long handle);

    public static void main(String[] args) throws Exception {
        if (args.length != 3) throw new IllegalArgumentException("INPUT OUTPUT LOOPS");
        Path destination = Path.of(args[1]);
        int loops = Integer.parseInt(args[2]);
        if (Files.exists(destination) || loops < 1 || loops > 10000)
            throw new IllegalArgumentException("invalid output/loops");
        byte[] bytes = Files.readAllBytes(Path.of(args[0]));
        if (bytes.length < 1 || bytes.length > 1024 * 1024)
            throw new IllegalArgumentException("invalid public packet size");
        ByteBuffer source = ByteBuffer.allocateDirect(bytes.length);
        source.put(bytes).flip();
        ByteBuffer result = ByteBuffer.allocateDirect(bytes.length + 1024);
        long compressor = create(6);
        if (compressor == 0) throw new IllegalStateException("native compressor unavailable");
        try {
            for (int i = 0; i < 100; i++)
                if (compress(compressor, source, bytes.length, result) < 1)
                    throw new IllegalStateException("native warm-up failed");
            long start = System.nanoTime();
            int written = 0;
            for (int i = 0; i < loops; i++) {
                written = compress(compressor, source, bytes.length, result);
                if (written < 1) throw new IllegalStateException("native compression failed");
            }
            double millis = (System.nanoTime() - start) / 1_000_000.0;
            byte[] compressed = new byte[written];
            result.position(0);
            result.get(compressed);
            Files.write(destination, compressed);
            System.out.printf("JNI_ZLIB_MS=%.3f loops=%d source_bytes=%d compressed_bytes=%d%n",
                              millis, loops, bytes.length, written);
        } finally {
            destroy(compressor);
        }
    }
}
