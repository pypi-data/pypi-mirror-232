// Copyright 2022, 2023 Peter Dimov
// Distributed under the Boost Software License, Version 1.0.
// https://www.boost.org/LICENSE_1_0.txt

#ifndef BOOST_HASH_DETAIL_MULX_HPP
#define BOOST_HASH_DETAIL_MULX_HPP

#include <boost/cstdint.hpp>
#if defined(_MSC_VER)
# include <intrin.h>
#endif

namespace boost
{
namespace hash_detail
{

#if defined(_MSC_VER) && defined(_M_X64) && !defined(__clang__)

__forceinline boost::uint64_t mulx( boost::uint64_t x, boost::uint64_t y )
{
    boost::uint64_t r2;
    boost::uint64_t r = _umul128( x, y, &r2 );
    return r ^ r2;
}

#elif defined(_MSC_VER) && defined(_M_ARM64) && !defined(__clang__)

__forceinline boost::uint64_t mulx( boost::uint64_t x, boost::uint64_t y )
{
    boost::uint64_t r = x * y;
    boost::uint64_t r2 = __umulh( x, y );
    return r ^ r2;
}

#elif defined(__SIZEOF_INT128__)

inline boost::uint64_t mulx( boost::uint64_t x, boost::uint64_t y )
{
    __uint128_t r = static_cast<__uint128_t>( x ) * y;
    return static_cast<boost::uint64_t>( r ) ^ static_cast<boost::uint64_t>( r >> 64 );
}

#else

inline boost::uint64_t mulx( boost::uint64_t x, boost::uint64_t y )
{
    boost::uint64_t x1 = static_cast<boost::uint32_t>( x );
    boost::uint64_t x2 = x >> 32;

    boost::uint64_t y1 = static_cast<boost::uint32_t>( y );
    boost::uint64_t y2 = y >> 32;

    boost::uint64_t r3 = x2 * y2;

    boost::uint64_t r2a = x1 * y2;

    r3 += r2a >> 32;

    boost::uint64_t r2b = x2 * y1;

    r3 += r2b >> 32;

    boost::uint64_t r1 = x1 * y1;

    boost::uint64_t r2 = (r1 >> 32) + static_cast<boost::uint32_t>( r2a ) + static_cast<boost::uint32_t>( r2b );

    r1 = (r2 << 32) + static_cast<boost::uint32_t>( r1 );
    r3 += r2 >> 32;

    return r1 ^ r3;
}

#endif

} // namespace hash_detail
} // namespace boost

#endif // #ifndef BOOST_HASH_DETAIL_MULX_HPP
