/* JNI research shim; no server.jar integration. libdeflate is MIT-licensed upstream. */
#include <jni.h>
#include <stdint.h>
#include "libdeflate.h"

JNIEXPORT jlong JNICALL Java_NativeDeflater_create(JNIEnv *env, jclass type, jint level) {
    (void)env; (void)type;
    return (jlong)(intptr_t)libdeflate_alloc_compressor(level);
}

JNIEXPORT jint JNICALL Java_NativeDeflater_bound(JNIEnv *env, jclass type,
        jlong handle, jint length) {
    (void)env; (void)type;
    struct libdeflate_compressor *compressor = (void *)(intptr_t)handle;
    if (!compressor || length < 0) return -1;
    size_t needed = libdeflate_zlib_compress_bound(compressor, (size_t)length);
    return needed > 0 && needed <= INT32_MAX ? (jint)needed : -1;
}

JNIEXPORT jint JNICALL Java_NativeDeflater_compress(JNIEnv *env, jclass type,
        jlong handle, jobject input, jint length, jobject output) {
    (void)type;
    struct libdeflate_compressor *compressor = (void *)(intptr_t)handle;
    if (!compressor || !input || !output || length < 0) return -1;
    void *src = (*env)->GetDirectBufferAddress(env, input);
    void *dst = (*env)->GetDirectBufferAddress(env, output);
    jlong src_cap = (*env)->GetDirectBufferCapacity(env, input);
    jlong dst_cap = (*env)->GetDirectBufferCapacity(env, output);
    if (!src || !dst || src_cap < length ||
            dst_cap <= 0 || (size_t)dst_cap < libdeflate_zlib_compress_bound(compressor, (size_t)length))
        return -1;
    size_t written = libdeflate_zlib_compress(compressor, src, (size_t)length,
                                             dst, (size_t)dst_cap);
    return written > 0 && written <= INT32_MAX ? (jint)written : -1;
}

JNIEXPORT void JNICALL Java_NativeDeflater_destroy(JNIEnv *env, jclass type, jlong handle) {
    (void)env; (void)type;
    libdeflate_free_compressor((void *)(intptr_t)handle);
}
