// Private-lab research only. Rust FFI to MIT libdeflate; NOT part of the JVM.
// Source: https://github.com/ebiggers/libdeflate at pinned workflow commit.
use std::ffi::c_void;
use std::fs;
use std::hint::black_box;
use std::path::Path;
use std::time::Instant;

#[link(name = "deflate", kind = "static")]
extern "C" {
    fn libdeflate_alloc_compressor(level: i32) -> *mut c_void;
    fn libdeflate_zlib_compress_bound(compressor: *mut c_void, len: usize) -> usize;
    fn libdeflate_zlib_compress(compressor: *mut c_void, input: *const c_void,
                               input_len: usize, output: *mut c_void, output_len: usize) -> usize;
    fn libdeflate_free_compressor(compressor: *mut c_void);
}

struct Compressor(*mut c_void);
impl Drop for Compressor {
    fn drop(&mut self) { unsafe { libdeflate_free_compressor(self.0) }; }
}

fn run(input: &Path, output: &Path, loops: usize) -> Result<(), Box<dyn std::error::Error>> {
    if output.exists() || loops == 0 || loops > 10_000 { return Err("invalid output/loops".into()); }
    let data = fs::read(input)?;
    if data.is_empty() || data.len() > 1024 * 1024 { return Err("invalid public packet size".into()); }
    let compressor = Compressor(unsafe { libdeflate_alloc_compressor(6) });
    if compressor.0.is_null() { return Err("compressor allocation failed".into()); }
    let bound = unsafe { libdeflate_zlib_compress_bound(compressor.0, data.len()) };
    if bound == 0 || bound > 2 * 1024 * 1024 { return Err("invalid zlib output bound".into()); }
    let mut compressed = vec![0u8; bound];
    let mut encode = || -> Result<usize, Box<dyn std::error::Error>> {
        let written = unsafe { libdeflate_zlib_compress(compressor.0, data.as_ptr().cast(),
                                                        data.len(), compressed.as_mut_ptr().cast(), bound) };
        if written == 0 { return Err("compression failed".into()); }
        Ok(black_box(written))
    };
    for _ in 0..100 { encode()?; }
    let start = Instant::now();
    let mut written = 0;
    for _ in 0..loops { written = encode()?; }
    let millis = start.elapsed().as_secs_f64() * 1000.0;
    fs::write(output, &compressed[..written])?;
    println!("RUST_ZLIB_MS={:.3} loops={} source_bytes={} compressed_bytes={}",
             millis, loops, data.len(), written);
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 4 { return Err("usage: RustLibdeflate INPUT OUTPUT LOOPS".into()); }
    run(Path::new(&args[1]), Path::new(&args[2]), args[3].parse()?)
}
