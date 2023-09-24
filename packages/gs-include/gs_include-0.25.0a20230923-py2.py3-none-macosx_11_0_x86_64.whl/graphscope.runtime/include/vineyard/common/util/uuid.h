/** Copyright 2020-2023 Alibaba Group Holding Limited.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#ifndef SRC_COMMON_UTIL_UUID_H_
#define SRC_COMMON_UTIL_UUID_H_

#include <sys/time.h>

#ifdef __MACH__
#include <mach/clock.h>
#include <mach/mach.h>
#endif

#include <cstdint>
#include <cstdlib>
#include <ctime>
#include <limits>
#include <string>

#include "common/util/base64.h"

namespace vineyard {

namespace detail {
namespace cycleclock {
static inline uint64_t timestamp_now() {
  struct timespec ts;
#ifdef __MACH__  // OS X does not have clock_gettime, use clock_get_time
  clock_serv_t clock_serv;
  mach_timespec_t mts;
  host_get_clock_service(mach_host_self(), CALENDAR_CLOCK, &clock_serv);
  clock_get_time(clock_serv, &mts);
  mach_port_deallocate(mach_task_self(), clock_serv);
  ts.tv_sec = mts.tv_sec;
  ts.tv_nsec = mts.tv_nsec;
#else
  clock_gettime(CLOCK_REALTIME, &ts);
#endif
  return static_cast<uint64_t>(ts.tv_sec) * static_cast<uint64_t>(1000000000) +
         static_cast<uint64_t>(ts.tv_nsec);
}

// the macro __VPP is used for codegen where libclang cannot process
// these headers without extra warnings.
#if !defined(__VPP)
// the platform-specific implementation is referred from google/benchmark
// project on Github, see also:
//
//  https://github.com/google/benchmark/blob/v1.1.0/src/cycleclock.h
static inline uint64_t now() {
#if defined(__i386__)
  int64_t ret;
  __asm__ volatile("rdtsc" : "=A"(ret));
  return static_cast<uint64_t>(ret);
#elif defined(__x86_64__) || defined(__amd64__)
  uint64_t low, high;
  __asm__ volatile("rdtsc" : "=a"(low), "=d"(high));
  return static_cast<uint64_t>((high << 32) | low);
#elif defined(__ia64__)
  int64_t itc;
  asm("mov %0 = ar.itc" : "=r"(itc));
  return static_cast<uint64_t>(itc);
#elif defined(__aarch64__)
  // System timer of ARMv8 runs at a different frequency than the CPU's.
  // The frequency is fixed, typically in the range 1-50MHz.  It can be
  // read at CNTFRQ special register.  We assume the OS has set up
  // the virtual timer properly.
  int64_t virtual_timer_value;
  asm volatile("mrs %0, cntvct_el0" : "=r"(virtual_timer_value));
  return static_cast<uint64_t>(virtual_timer_value);
#elif defined(__ARM_ARCH)
#if (__ARM_ARCH >= 6)  // V6 is the earliest arch that has a standard cyclecount
  uint32_t pmccntr;
  uint32_t pmuseren;
  uint32_t pmcntenset;
  // Read the user mode perf monitor counter access permissions.
  asm volatile("mrc p15, 0, %0, c9, c14, 0" : "=r"(pmuseren));
  if (pmuseren & 1) {  // Allows reading perfmon counters for user mode code.
    asm volatile("mrc p15, 0, %0, c9, c12, 1" : "=r"(pmcntenset));
    if (pmcntenset & 0x80000000ul) {  // Is it counting?
      asm volatile("mrc p15, 0, %0, c9, c13, 0" : "=r"(pmccntr));
      // The counter is set up to count every 64th cycle
      return static_cast<uint64_t>(pmccntr) * 64;  // Should optimize to << 6
    }
  }
#endif
  return timestamp_now();
#else
  // mips apparently only allows rdtsc for superusers, so we fall
  // back to gettimeofday.  It's possible clock_gettime would be better.
  return timestamp_now();
#endif
}
#else
inline int64_t now() { return timestamp_now(); }
#endif
}  // namespace cycleclock
}  // namespace detail

/**
 * @brief ObjectID is an opaque type for vineyard's object id. The object ID is
 * generated by vineyard server, the underlying type of ObjectID is a 64-bit
 * unsigned integer.
 */
using ObjectID = uint64_t;

/**
 * @brief Signature is an opaque type for vineyard's object. The signature of
 * an object keep unchanged during migration. The underlying type of Signature
 * is a 64-bit unsigned integer.
 */
using Signature = uint64_t;

/**
 * @brief InstanceID is an opaque type for vineyard's instance. The
 * underlying type of Instance is a 64-bit unsigned integer.
 */
using InstanceID = uint64_t;

/**
 * @brief SessionID is an opaque type for vineyard's Session. The
 * underlying type of SessionID is a 64-bit unsigned integer.
 */
using SessionID = int64_t;

/**
 * @brief PlasmaID is an opaque type for vineyard's PlasmaPayload. The
 * underlying type of PlasmaID is base64 string for compatibility.
 */
using PlasmaID = std::string;

/*
 *  @brief Make empty blob and preallocate blob always mapping to the same place
 *         Others will be mapped randomly between
 * (0x8000000000000000UL,0xFFFFFFFFFFFFFFFFUL) exclusively.
 */
inline ObjectID GenerateBlobID(const uintptr_t ptr) {
  if (ptr == 0x8000000000000000UL ||
      ptr == std::numeric_limits<uintptr_t>::max()) {
    return static_cast<uint64_t>(ptr) | 0x8000000000000000UL;
  }
  auto ts = detail::cycleclock::now() % (0x7FFFFFFFFFFFFFFFUL - 2) + 1;
  return (0x7FFFFFFFFFFFFFFFUL & static_cast<uint64_t>(ts)) |
         0x8000000000000000UL;
}

inline SessionID GenerateSessionID() {
  return 0x7FFFFFFFFFFFFFFFUL & detail::cycleclock::now();
}

inline ObjectID GenerateObjectID() {
  return 0x7FFFFFFFFFFFFFFFUL & detail::cycleclock::now();
}

inline ObjectID GenerateSignature() {
  return 0x7FFFFFFFFFFFFFFFUL & detail::cycleclock::now();
}

inline bool IsBlob(ObjectID id) { return id & 0x8000000000000000UL; }

const std::string ObjectIDToString(const ObjectID id);

const std::string ObjectIDToString(const PlasmaID id);

inline std::string const PlasmaIDToString(PlasmaID const plasma_id) {
  return base64_decode(std::string(plasma_id));
}

inline ObjectID ObjectIDFromString(const std::string& s) {
  return strtoull(s.c_str() + 1, nullptr, 16);
}

inline ObjectID ObjectIDFromString(const char* s) {
  return strtoull(s + 1, nullptr, 16);
}

// TODO base64 encoding
inline PlasmaID PlasmaIDFromString(std::string const& s) {
  return PlasmaID(base64_encode(s));
}

inline PlasmaID PlasmaIDFromString(const char* s) {
  return PlasmaID(base64_encode(s));
}

constexpr inline SessionID RootSessionID() { return 0x0000000000000000UL; }

const std::string SessionIDToString(const SessionID id);

inline SessionID SessionIDFromString(const std::string& s) {
  return strtoull(s.c_str() + 1, nullptr, 16);
}

inline SessionID SessionIDFromString(const char* s) {
  return strtoull(s + 1, nullptr, 16);
}

[[deprecated(
    "For backwards-compatibility, will be removed in 1.0.")]] inline const std::
    string
    VYObjectIDToString(const ObjectID id) {
  return ObjectIDToString(id);
}

[[deprecated(
    "For backwards-compatibility, will be removed in 1.0.")]] inline ObjectID
VYObjectIDFromString(const std::string& s) {
  return ObjectIDFromString(s);
}

[[deprecated(
    "For backwards-compatibility, will be removed in 1.0.")]] inline ObjectID
VYObjectIDFromString(const char* s) {
  return ObjectIDFromString(s);
}

const std::string SignatureToString(const Signature id);

inline Signature SignatureFromString(const std::string& s) {
  return strtoull(s.c_str() + 1, nullptr, 16);
}

inline Signature SignatureFromString(const char* s) {
  return strtoull(s + 1, nullptr, 16);
}

inline ObjectID InvalidObjectID() {
  return std::numeric_limits<ObjectID>::max();
}

inline ObjectID InvalidSignature() {
  return std::numeric_limits<Signature>::max();
}

inline InstanceID UnspecifiedInstanceID() {
  return std::numeric_limits<InstanceID>::max();
}

template <typename ID>
inline ID GenerateBlobID(uintptr_t ptr);

template <>
inline ObjectID GenerateBlobID<ObjectID>(uintptr_t ptr) {
  return GenerateBlobID(ptr);
}

template <>
inline PlasmaID GenerateBlobID<PlasmaID>(uintptr_t ptr) {
  return PlasmaIDFromString(ObjectIDToString(ObjectID(GenerateBlobID(ptr))));
}

template <typename ID>
inline ID GenerateBlobID(const void* ptr) {
  return GenerateBlobID(reinterpret_cast<uintptr_t>(ptr));
}

template <typename ID = ObjectID>
ID EmptyBlobID() {
  return GenerateBlobID<ID>(0x8000000000000000UL);
}

template <typename ID>
std::string IDToString(ID id);

template <>
inline std::string IDToString<ObjectID>(ObjectID id) {
  return ObjectIDToString(id);
}

template <>
inline std::string IDToString<PlasmaID>(PlasmaID id) {
  return PlasmaIDToString(id);
}

}  // namespace vineyard

#endif  // SRC_COMMON_UTIL_UUID_H_
