// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: types.proto

#ifndef GOOGLE_PROTOBUF_INCLUDED_types_2eproto_2epb_2eh
#define GOOGLE_PROTOBUF_INCLUDED_types_2eproto_2epb_2eh

#include <limits>
#include <string>
#include <type_traits>

#include "google/protobuf/port_def.inc"
#if PROTOBUF_VERSION < 4024000
#error "This file was generated by a newer version of protoc which is"
#error "incompatible with your Protocol Buffer headers. Please update"
#error "your headers."
#endif  // PROTOBUF_VERSION

#if 4024003 < PROTOBUF_MIN_PROTOC_VERSION
#error "This file was generated by an older version of protoc which is"
#error "incompatible with your Protocol Buffer headers. Please"
#error "regenerate this file with a newer version of protoc."
#endif  // PROTOBUF_MIN_PROTOC_VERSION
#include "google/protobuf/port_undef.inc"
#include "google/protobuf/io/coded_stream.h"
#include "google/protobuf/arena.h"
#include "google/protobuf/arenastring.h"
#include "google/protobuf/generated_message_tctable_decl.h"
#include "google/protobuf/generated_message_util.h"
#include "google/protobuf/metadata_lite.h"
#include "google/protobuf/generated_message_reflection.h"
#include "google/protobuf/message.h"
#include "google/protobuf/repeated_field.h"  // IWYU pragma: export
#include "google/protobuf/extension_set.h"  // IWYU pragma: export
#include "google/protobuf/generated_enum_reflection.h"
#include "google/protobuf/unknown_field_set.h"
#include "google/protobuf/any.pb.h"
// @@protoc_insertion_point(includes)

// Must be included last.
#include "google/protobuf/port_def.inc"

#define PROTOBUF_INTERNAL_EXPORT_types_2eproto

namespace google {
namespace protobuf {
namespace internal {
class AnyMetadata;
}  // namespace internal
}  // namespace protobuf
}  // namespace google

// Internal implementation detail -- do not use these members.
struct TableStruct_types_2eproto {
  static const ::uint32_t offsets[];
};
extern const ::google::protobuf::internal::DescriptorTable
    descriptor_table_types_2eproto;
namespace gs {
namespace rpc {
class QueryArgs;
struct QueryArgsDefaultTypeInternal;
extern QueryArgsDefaultTypeInternal _QueryArgs_default_instance_;
}  // namespace rpc
}  // namespace gs
namespace google {
namespace protobuf {
}  // namespace protobuf
}  // namespace google

namespace gs {
namespace rpc {
enum ClusterType : int {
  HOSTS = 0,
  K8S = 1,
  OPERATOR = 2,
  UNDEFINED = 100,
  ClusterType_INT_MIN_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::min(),
  ClusterType_INT_MAX_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::max(),
};

bool ClusterType_IsValid(int value);
constexpr ClusterType ClusterType_MIN = static_cast<ClusterType>(0);
constexpr ClusterType ClusterType_MAX = static_cast<ClusterType>(100);
constexpr int ClusterType_ARRAYSIZE = 100 + 1;
const ::google::protobuf::EnumDescriptor*
ClusterType_descriptor();
template <typename T>
const std::string& ClusterType_Name(T value) {
  static_assert(std::is_same<T, ClusterType>::value ||
                    std::is_integral<T>::value,
                "Incorrect type passed to ClusterType_Name().");
  return ::google::protobuf::internal::NameOfEnum(ClusterType_descriptor(), value);
}
inline bool ClusterType_Parse(absl::string_view name, ClusterType* value) {
  return ::google::protobuf::internal::ParseNamedEnum<ClusterType>(
      ClusterType_descriptor(), name, value);
}
enum DataType : int {
  NULLVALUE = 0,
  INT8 = 1,
  INT16 = 2,
  INT32 = 3,
  INT64 = 4,
  INT128 = 5,
  UINT8 = 6,
  UINT16 = 7,
  UINT32 = 8,
  UINT64 = 9,
  UINT128 = 10,
  INT = 11,
  LONG = 12,
  LONGLONG = 13,
  UINT = 14,
  ULONG = 15,
  ULONGLONG = 16,
  FLOAT = 18,
  DOUBLE = 19,
  BOOLEAN = 20,
  STRING = 21,
  DATETIME = 22,
  LIST = 23,
  INVALID = 536870911,
  DataType_INT_MIN_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::min(),
  DataType_INT_MAX_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::max(),
};

bool DataType_IsValid(int value);
constexpr DataType DataType_MIN = static_cast<DataType>(0);
constexpr DataType DataType_MAX = static_cast<DataType>(536870911);
constexpr int DataType_ARRAYSIZE = 536870911 + 1;
const ::google::protobuf::EnumDescriptor*
DataType_descriptor();
template <typename T>
const std::string& DataType_Name(T value) {
  static_assert(std::is_same<T, DataType>::value ||
                    std::is_integral<T>::value,
                "Incorrect type passed to DataType_Name().");
  return ::google::protobuf::internal::NameOfEnum(DataType_descriptor(), value);
}
inline bool DataType_Parse(absl::string_view name, DataType* value) {
  return ::google::protobuf::internal::ParseNamedEnum<DataType>(
      DataType_descriptor(), name, value);
}
enum Direction : int {
  NONE = 0,
  IN = 1,
  OUT = 2,
  Direction_INT_MIN_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::min(),
  Direction_INT_MAX_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::max(),
};

bool Direction_IsValid(int value);
constexpr Direction Direction_MIN = static_cast<Direction>(0);
constexpr Direction Direction_MAX = static_cast<Direction>(2);
constexpr int Direction_ARRAYSIZE = 2 + 1;
const ::google::protobuf::EnumDescriptor*
Direction_descriptor();
template <typename T>
const std::string& Direction_Name(T value) {
  static_assert(std::is_same<T, Direction>::value ||
                    std::is_integral<T>::value,
                "Incorrect type passed to Direction_Name().");
  return Direction_Name(static_cast<Direction>(value));
}
template <>
inline const std::string& Direction_Name(Direction value) {
  return ::google::protobuf::internal::NameOfDenseEnum<Direction_descriptor,
                                                 0, 2>(
      static_cast<int>(value));
}
inline bool Direction_Parse(absl::string_view name, Direction* value) {
  return ::google::protobuf::internal::ParseNamedEnum<Direction>(
      Direction_descriptor(), name, value);
}
enum OutputType : int {
  GRAPH = 0,
  APP = 1,
  BOUND_APP = 2,
  RESULTS = 3,
  TENSOR = 4,
  DATAFRAME = 5,
  VINEYARD_TENSOR = 6,
  VINEYARD_DATAFRAME = 7,
  INTERACTIVE_QUERY = 8,
  LEARNING_GRAPH = 10,
  NULL_OUTPUT = 101,
  OutputType_INT_MIN_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::min(),
  OutputType_INT_MAX_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::max(),
};

bool OutputType_IsValid(int value);
constexpr OutputType OutputType_MIN = static_cast<OutputType>(0);
constexpr OutputType OutputType_MAX = static_cast<OutputType>(101);
constexpr int OutputType_ARRAYSIZE = 101 + 1;
const ::google::protobuf::EnumDescriptor*
OutputType_descriptor();
template <typename T>
const std::string& OutputType_Name(T value) {
  static_assert(std::is_same<T, OutputType>::value ||
                    std::is_integral<T>::value,
                "Incorrect type passed to OutputType_Name().");
  return ::google::protobuf::internal::NameOfEnum(OutputType_descriptor(), value);
}
inline bool OutputType_Parse(absl::string_view name, OutputType* value) {
  return ::google::protobuf::internal::ParseNamedEnum<OutputType>(
      OutputType_descriptor(), name, value);
}
enum OperationType : int {
  CREATE_GRAPH = 0,
  BIND_APP = 1,
  CREATE_APP = 2,
  MODIFY_VERTICES = 3,
  MODIFY_EDGES = 4,
  RUN_APP = 5,
  UNLOAD_APP = 6,
  UNLOAD_GRAPH = 7,
  REPARTITION = 8,
  TRANSFORM_GRAPH = 9,
  REPORT_GRAPH = 10,
  PROJECT_GRAPH = 11,
  PROJECT_TO_SIMPLE = 12,
  COPY_GRAPH = 13,
  ADD_VERTICES = 14,
  ADD_EDGES = 15,
  ADD_LABELS = 16,
  TO_DIRECTED = 17,
  TO_UNDIRECTED = 18,
  CLEAR_EDGES = 19,
  CLEAR_GRAPH = 20,
  VIEW_GRAPH = 21,
  INDUCE_SUBGRAPH = 22,
  UNLOAD_CONTEXT = 23,
  ARCHIVE_GRAPH = 24,
  SERIALIZE_GRAPH = 25,
  DESERIALIZE_GRAPH = 26,
  CONSOLIDATE_COLUMNS = 27,
  SUBGRAPH = 32,
  DATA_SOURCE = 46,
  DATA_SINK = 47,
  CONTEXT_TO_NUMPY = 50,
  CONTEXT_TO_DATAFRAME = 51,
  TO_VINEYARD_TENSOR = 53,
  TO_VINEYARD_DATAFRAME = 54,
  ADD_COLUMN = 55,
  GRAPH_TO_NUMPY = 56,
  GRAPH_TO_DATAFRAME = 57,
  REGISTER_GRAPH_TYPE = 58,
  GET_CONTEXT_DATA = 59,
  OUTPUT = 60,
  FROM_NUMPY = 80,
  FROM_DATAFRAME = 81,
  FROM_FILE = 82,
  GET_ENGINE_CONFIG = 90,
  OperationType_INT_MIN_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::min(),
  OperationType_INT_MAX_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::max(),
};

bool OperationType_IsValid(int value);
constexpr OperationType OperationType_MIN = static_cast<OperationType>(0);
constexpr OperationType OperationType_MAX = static_cast<OperationType>(90);
constexpr int OperationType_ARRAYSIZE = 90 + 1;
const ::google::protobuf::EnumDescriptor*
OperationType_descriptor();
template <typename T>
const std::string& OperationType_Name(T value) {
  static_assert(std::is_same<T, OperationType>::value ||
                    std::is_integral<T>::value,
                "Incorrect type passed to OperationType_Name().");
  return ::google::protobuf::internal::NameOfEnum(OperationType_descriptor(), value);
}
inline bool OperationType_Parse(absl::string_view name, OperationType* value) {
  return ::google::protobuf::internal::ParseNamedEnum<OperationType>(
      OperationType_descriptor(), name, value);
}
enum ParamKey : int {
  GRAPH_NAME = 0,
  DST_GRAPH_NAME = 1,
  CONTEXT_KEY = 2,
  GRAPH_TYPE = 3,
  DST_GRAPH_TYPE = 4,
  OID_TYPE = 5,
  VID_TYPE = 6,
  V_DATA_TYPE = 7,
  E_DATA_TYPE = 8,
  V_LABEL_ID = 9,
  E_LABEL_ID = 10,
  V_PROP_ID = 11,
  E_PROP_ID = 12,
  LINE_PARSER = 13,
  E_FILE = 14,
  V_FILE = 15,
  VERTEX_LABEL_NUM = 16,
  EDGE_LABEL_NUM = 17,
  DIRECTED = 18,
  V_PROP_KEY = 19,
  E_PROP_KEY = 20,
  V_DEFAULT_VAL = 21,
  E_DEFAULT_VAL = 22,
  GRAPH_TEMPLATE_CLASS = 23,
  REPARTITION_STRATEGY = 24,
  PARAM = 26,
  DISTRIBUTED = 27,
  SCHEMA_PATH = 31,
  GIE_GREMLIN_QUERY_MESSAGE = 35,
  GIE_GREMLIN_REQUEST_OPTIONS = 36,
  GIE_GREMLIN_FETCH_RESULT_TYPE = 37,
  APP_SIGNATURE = 40,
  GRAPH_SIGNATURE = 41,
  IS_FROM_VINEYARD_ID = 42,
  VINEYARD_ID = 43,
  VINEYARD_NAME = 44,
  VERTEX_MAP_TYPE = 45,
  COMPACT_EDGES = 46,
  USE_PERFECT_HASH = 47,
  CONSOLIDATE_COLUMNS_LABEL = 48,
  CONSOLIDATE_COLUMNS_COLUMNS = 49,
  CONSOLIDATE_COLUMNS_RESULT_COLUMN = 50,
  VERTEX_COLLECTIONS = 51,
  EDGE_COLLECTIONS = 52,
  GLE_HANDLE = 60,
  GLE_CONFIG = 61,
  GLE_GEN_LABELS = 62,
  IS_FROM_GAR = 70,
  GRAPH_INFO_PATH = 71,
  APP_NAME = 100,
  APP_ALGO = 101,
  APP_LIBRARY_PATH = 102,
  OUTPUT_PREFIX = 103,
  VERTEX_RANGE = 104,
  SELECTOR = 105,
  AXIS = 106,
  GAR = 107,
  TYPE_SIGNATURE = 108,
  CMAKE_EXTRA_OPTIONS = 109,
  REPORT_TYPE = 200,
  MODIFY_TYPE = 201,
  NODE = 202,
  EDGE = 203,
  FID = 204,
  LID = 205,
  EDGE_KEY = 206,
  NODES = 207,
  EDGES = 208,
  COPY_TYPE = 209,
  VIEW_TYPE = 210,
  ARROW_PROPERTY_DEFINITION = 300,
  PROTOCOL = 301,
  VALUES = 302,
  VID = 303,
  SRC_VID = 304,
  DST_VID = 305,
  LABEL = 306,
  SRC_LABEL = 307,
  DST_LABEL = 308,
  PROPERTIES = 309,
  LOADER = 310,
  LOAD_STRATEGY = 311,
  ROW_NUM = 312,
  COLUMN_NUM = 313,
  SUB_LABEL = 315,
  GENERATE_EID = 316,
  DEFAULT_LABEL_ID = 317,
  GID = 318,
  RETAIN_OID = 319,
  STORAGE_OPTIONS = 321,
  READ_OPTIONS = 322,
  FD = 323,
  SOURCE = 324,
  WRITE_OPTIONS = 325,
  CHUNK_NAME = 341,
  CHUNK_TYPE = 342,
  GRAPH_LIBRARY_PATH = 400,
  GRAPH_SERIALIZATION_PATH = 401,
  VFORMAT = 500,
  EFORMAT = 501,
  JAVA_CLASS_PATH = 502,
  JVM_OPTS = 503,
  ParamKey_INT_MIN_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::min(),
  ParamKey_INT_MAX_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::max(),
};

bool ParamKey_IsValid(int value);
constexpr ParamKey ParamKey_MIN = static_cast<ParamKey>(0);
constexpr ParamKey ParamKey_MAX = static_cast<ParamKey>(503);
constexpr int ParamKey_ARRAYSIZE = 503 + 1;
const ::google::protobuf::EnumDescriptor*
ParamKey_descriptor();
template <typename T>
const std::string& ParamKey_Name(T value) {
  static_assert(std::is_same<T, ParamKey>::value ||
                    std::is_integral<T>::value,
                "Incorrect type passed to ParamKey_Name().");
  return ::google::protobuf::internal::NameOfEnum(ParamKey_descriptor(), value);
}
inline bool ParamKey_Parse(absl::string_view name, ParamKey* value) {
  return ::google::protobuf::internal::ParseNamedEnum<ParamKey>(
      ParamKey_descriptor(), name, value);
}
enum ModifyType : int {
  NX_ADD_NODES = 0,
  NX_ADD_EDGES = 1,
  NX_DEL_NODES = 2,
  NX_DEL_EDGES = 3,
  NX_UPDATE_NODES = 4,
  NX_UPDATE_EDGES = 5,
  ModifyType_INT_MIN_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::min(),
  ModifyType_INT_MAX_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::max(),
};

bool ModifyType_IsValid(int value);
constexpr ModifyType ModifyType_MIN = static_cast<ModifyType>(0);
constexpr ModifyType ModifyType_MAX = static_cast<ModifyType>(5);
constexpr int ModifyType_ARRAYSIZE = 5 + 1;
const ::google::protobuf::EnumDescriptor*
ModifyType_descriptor();
template <typename T>
const std::string& ModifyType_Name(T value) {
  static_assert(std::is_same<T, ModifyType>::value ||
                    std::is_integral<T>::value,
                "Incorrect type passed to ModifyType_Name().");
  return ModifyType_Name(static_cast<ModifyType>(value));
}
template <>
inline const std::string& ModifyType_Name(ModifyType value) {
  return ::google::protobuf::internal::NameOfDenseEnum<ModifyType_descriptor,
                                                 0, 5>(
      static_cast<int>(value));
}
inline bool ModifyType_Parse(absl::string_view name, ModifyType* value) {
  return ::google::protobuf::internal::ParseNamedEnum<ModifyType>(
      ModifyType_descriptor(), name, value);
}
enum ReportType : int {
  NODE_NUM = 0,
  EDGE_NUM = 1,
  HAS_NODE = 2,
  HAS_EDGE = 3,
  NODE_DATA = 4,
  EDGE_DATA = 5,
  SUCCS_BY_NODE = 6,
  PREDS_BY_NODE = 7,
  SELFLOOPS_NUM = 8,
  NODE_ID_CACHE_BY_GID = 9,
  NODE_ATTR_CACHE_BY_GID = 10,
  SUCC_BY_GID = 11,
  PRED_BY_GID = 12,
  SUCC_ATTR_BY_GID = 13,
  PRED_ATTR_BY_GID = 14,
  SUCC_ATTR_BY_NODE = 15,
  PRED_ATTR_BY_NODE = 16,
  ReportType_INT_MIN_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::min(),
  ReportType_INT_MAX_SENTINEL_DO_NOT_USE_ =
      std::numeric_limits<::int32_t>::max(),
};

bool ReportType_IsValid(int value);
constexpr ReportType ReportType_MIN = static_cast<ReportType>(0);
constexpr ReportType ReportType_MAX = static_cast<ReportType>(16);
constexpr int ReportType_ARRAYSIZE = 16 + 1;
const ::google::protobuf::EnumDescriptor*
ReportType_descriptor();
template <typename T>
const std::string& ReportType_Name(T value) {
  static_assert(std::is_same<T, ReportType>::value ||
                    std::is_integral<T>::value,
                "Incorrect type passed to ReportType_Name().");
  return ReportType_Name(static_cast<ReportType>(value));
}
template <>
inline const std::string& ReportType_Name(ReportType value) {
  return ::google::protobuf::internal::NameOfDenseEnum<ReportType_descriptor,
                                                 0, 16>(
      static_cast<int>(value));
}
inline bool ReportType_Parse(absl::string_view name, ReportType* value) {
  return ::google::protobuf::internal::ParseNamedEnum<ReportType>(
      ReportType_descriptor(), name, value);
}

// ===================================================================


// -------------------------------------------------------------------

class QueryArgs final :
    public ::google::protobuf::Message /* @@protoc_insertion_point(class_definition:gs.rpc.QueryArgs) */ {
 public:
  inline QueryArgs() : QueryArgs(nullptr) {}
  ~QueryArgs() override;
  template<typename = void>
  explicit PROTOBUF_CONSTEXPR QueryArgs(::google::protobuf::internal::ConstantInitialized);

  QueryArgs(const QueryArgs& from);
  QueryArgs(QueryArgs&& from) noexcept
    : QueryArgs() {
    *this = ::std::move(from);
  }

  inline QueryArgs& operator=(const QueryArgs& from) {
    CopyFrom(from);
    return *this;
  }
  inline QueryArgs& operator=(QueryArgs&& from) noexcept {
    if (this == &from) return *this;
    if (GetOwningArena() == from.GetOwningArena()
  #ifdef PROTOBUF_FORCE_COPY_IN_MOVE
        && GetOwningArena() != nullptr
  #endif  // !PROTOBUF_FORCE_COPY_IN_MOVE
    ) {
      InternalSwap(&from);
    } else {
      CopyFrom(from);
    }
    return *this;
  }

  inline const ::google::protobuf::UnknownFieldSet& unknown_fields() const {
    return _internal_metadata_.unknown_fields<::google::protobuf::UnknownFieldSet>(::google::protobuf::UnknownFieldSet::default_instance);
  }
  inline ::google::protobuf::UnknownFieldSet* mutable_unknown_fields() {
    return _internal_metadata_.mutable_unknown_fields<::google::protobuf::UnknownFieldSet>();
  }

  static const ::google::protobuf::Descriptor* descriptor() {
    return GetDescriptor();
  }
  static const ::google::protobuf::Descriptor* GetDescriptor() {
    return default_instance().GetMetadata().descriptor;
  }
  static const ::google::protobuf::Reflection* GetReflection() {
    return default_instance().GetMetadata().reflection;
  }
  static const QueryArgs& default_instance() {
    return *internal_default_instance();
  }
  static inline const QueryArgs* internal_default_instance() {
    return reinterpret_cast<const QueryArgs*>(
               &_QueryArgs_default_instance_);
  }
  static constexpr int kIndexInFileMessages =
    0;

  friend void swap(QueryArgs& a, QueryArgs& b) {
    a.Swap(&b);
  }
  inline void Swap(QueryArgs* other) {
    if (other == this) return;
  #ifdef PROTOBUF_FORCE_COPY_IN_SWAP
    if (GetOwningArena() != nullptr &&
        GetOwningArena() == other->GetOwningArena()) {
   #else  // PROTOBUF_FORCE_COPY_IN_SWAP
    if (GetOwningArena() == other->GetOwningArena()) {
  #endif  // !PROTOBUF_FORCE_COPY_IN_SWAP
      InternalSwap(other);
    } else {
      ::google::protobuf::internal::GenericSwap(this, other);
    }
  }
  void UnsafeArenaSwap(QueryArgs* other) {
    if (other == this) return;
    ABSL_DCHECK(GetOwningArena() == other->GetOwningArena());
    InternalSwap(other);
  }

  // implements Message ----------------------------------------------

  QueryArgs* New(::google::protobuf::Arena* arena = nullptr) const final {
    return CreateMaybeMessage<QueryArgs>(arena);
  }
  using ::google::protobuf::Message::CopyFrom;
  void CopyFrom(const QueryArgs& from);
  using ::google::protobuf::Message::MergeFrom;
  void MergeFrom( const QueryArgs& from) {
    QueryArgs::MergeImpl(*this, from);
  }
  private:
  static void MergeImpl(::google::protobuf::Message& to_msg, const ::google::protobuf::Message& from_msg);
  public:
  PROTOBUF_ATTRIBUTE_REINITIALIZES void Clear() final;
  bool IsInitialized() const final;

  ::size_t ByteSizeLong() const final;
  const char* _InternalParse(const char* ptr, ::google::protobuf::internal::ParseContext* ctx) final;
  ::uint8_t* _InternalSerialize(
      ::uint8_t* target, ::google::protobuf::io::EpsCopyOutputStream* stream) const final;
  int GetCachedSize() const final { return _impl_._cached_size_.Get(); }

  private:
  void SharedCtor(::google::protobuf::Arena* arena);
  void SharedDtor();
  void SetCachedSize(int size) const final;
  void InternalSwap(QueryArgs* other);

  private:
  friend class ::google::protobuf::internal::AnyMetadata;
  static ::absl::string_view FullMessageName() {
    return "gs.rpc.QueryArgs";
  }
  protected:
  explicit QueryArgs(::google::protobuf::Arena* arena);
  public:

  static const ClassData _class_data_;
  const ::google::protobuf::Message::ClassData*GetClassData() const final;

  ::google::protobuf::Metadata GetMetadata() const final;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  enum : int {
    kArgsFieldNumber = 1,
  };
  // repeated .google.protobuf.Any args = 1;
  int args_size() const;
  private:
  int _internal_args_size() const;

  public:
  void clear_args() ;
  ::google::protobuf::Any* mutable_args(int index);
  ::google::protobuf::RepeatedPtrField< ::google::protobuf::Any >*
      mutable_args();
  private:
  const ::google::protobuf::RepeatedPtrField<::google::protobuf::Any>& _internal_args() const;
  ::google::protobuf::RepeatedPtrField<::google::protobuf::Any>* _internal_mutable_args();
  public:
  const ::google::protobuf::Any& args(int index) const;
  ::google::protobuf::Any* add_args();
  const ::google::protobuf::RepeatedPtrField< ::google::protobuf::Any >&
      args() const;
  // @@protoc_insertion_point(class_scope:gs.rpc.QueryArgs)
 private:
  class _Internal;

  friend class ::google::protobuf::internal::TcParser;
  static const ::google::protobuf::internal::TcParseTable<0, 1, 1, 0, 2> _table_;
  template <typename T> friend class ::google::protobuf::Arena::InternalHelper;
  typedef void InternalArenaConstructable_;
  typedef void DestructorSkippable_;
  struct Impl_ {
    ::google::protobuf::RepeatedPtrField< ::google::protobuf::Any > args_;
    mutable ::google::protobuf::internal::CachedSize _cached_size_;
    PROTOBUF_TSAN_DECLARE_MEMBER
  };
  union { Impl_ _impl_; };
  friend struct ::TableStruct_types_2eproto;
};

// ===================================================================




// ===================================================================


#ifdef __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wstrict-aliasing"
#endif  // __GNUC__
// -------------------------------------------------------------------

// QueryArgs

// repeated .google.protobuf.Any args = 1;
inline int QueryArgs::_internal_args_size() const {
  return _internal_args().size();
}
inline int QueryArgs::args_size() const {
  return _internal_args_size();
}
inline ::google::protobuf::Any* QueryArgs::mutable_args(int index) {
  // @@protoc_insertion_point(field_mutable:gs.rpc.QueryArgs.args)
  return _internal_mutable_args()->Mutable(index);
}
inline ::google::protobuf::RepeatedPtrField< ::google::protobuf::Any >*
QueryArgs::mutable_args() {
  // @@protoc_insertion_point(field_mutable_list:gs.rpc.QueryArgs.args)
  PROTOBUF_TSAN_WRITE(&_impl_._tsan_detect_race);
  return _internal_mutable_args();
}
inline const ::google::protobuf::Any& QueryArgs::args(int index) const {
  // @@protoc_insertion_point(field_get:gs.rpc.QueryArgs.args)
    return _internal_args().Get(index);
}
inline ::google::protobuf::Any* QueryArgs::add_args() {
  PROTOBUF_TSAN_WRITE(&_impl_._tsan_detect_race);
  ::google::protobuf::Any* _add = _internal_mutable_args()->Add();
  // @@protoc_insertion_point(field_add:gs.rpc.QueryArgs.args)
  return _add;
}
inline const ::google::protobuf::RepeatedPtrField< ::google::protobuf::Any >&
QueryArgs::args() const {
  // @@protoc_insertion_point(field_list:gs.rpc.QueryArgs.args)
  return _internal_args();
}
inline const ::google::protobuf::RepeatedPtrField<::google::protobuf::Any>&
QueryArgs::_internal_args() const {
  PROTOBUF_TSAN_READ(&_impl_._tsan_detect_race);
  return _impl_.args_;
}
inline ::google::protobuf::RepeatedPtrField<::google::protobuf::Any>*
QueryArgs::_internal_mutable_args() {
  PROTOBUF_TSAN_READ(&_impl_._tsan_detect_race);
  return &_impl_.args_;
}

#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif  // __GNUC__

// @@protoc_insertion_point(namespace_scope)
}  // namespace rpc
}  // namespace gs


namespace google {
namespace protobuf {

template <>
struct is_proto_enum<::gs::rpc::ClusterType> : std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor<::gs::rpc::ClusterType>() {
  return ::gs::rpc::ClusterType_descriptor();
}
template <>
struct is_proto_enum<::gs::rpc::DataType> : std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor<::gs::rpc::DataType>() {
  return ::gs::rpc::DataType_descriptor();
}
template <>
struct is_proto_enum<::gs::rpc::Direction> : std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor<::gs::rpc::Direction>() {
  return ::gs::rpc::Direction_descriptor();
}
template <>
struct is_proto_enum<::gs::rpc::OutputType> : std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor<::gs::rpc::OutputType>() {
  return ::gs::rpc::OutputType_descriptor();
}
template <>
struct is_proto_enum<::gs::rpc::OperationType> : std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor<::gs::rpc::OperationType>() {
  return ::gs::rpc::OperationType_descriptor();
}
template <>
struct is_proto_enum<::gs::rpc::ParamKey> : std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor<::gs::rpc::ParamKey>() {
  return ::gs::rpc::ParamKey_descriptor();
}
template <>
struct is_proto_enum<::gs::rpc::ModifyType> : std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor<::gs::rpc::ModifyType>() {
  return ::gs::rpc::ModifyType_descriptor();
}
template <>
struct is_proto_enum<::gs::rpc::ReportType> : std::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor<::gs::rpc::ReportType>() {
  return ::gs::rpc::ReportType_descriptor();
}

}  // namespace protobuf
}  // namespace google

// @@protoc_insertion_point(global_scope)

#include "google/protobuf/port_undef.inc"

#endif  // GOOGLE_PROTOBUF_INCLUDED_types_2eproto_2epb_2eh
