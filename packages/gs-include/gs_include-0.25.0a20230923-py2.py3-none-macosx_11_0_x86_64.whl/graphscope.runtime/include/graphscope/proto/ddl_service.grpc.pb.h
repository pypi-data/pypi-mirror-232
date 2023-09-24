// Generated by the gRPC C++ plugin.
// If you make any local change, they will be lost.
// source: ddl_service.proto
// Original file comments:
// Copyright 2020 Alibaba Group Holding Limited. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
#ifndef GRPC_ddl_5fservice_2eproto__INCLUDED
#define GRPC_ddl_5fservice_2eproto__INCLUDED

#include "ddl_service.pb.h"

#include <functional>
#include <grpcpp/generic/async_generic_service.h>
#include <grpcpp/support/async_stream.h>
#include <grpcpp/support/async_unary_call.h>
#include <grpcpp/support/client_callback.h>
#include <grpcpp/client_context.h>
#include <grpcpp/completion_queue.h>
#include <grpcpp/support/message_allocator.h>
#include <grpcpp/support/method_handler.h>
#include <grpcpp/impl/proto_utils.h>
#include <grpcpp/impl/rpc_method.h>
#include <grpcpp/support/server_callback.h>
#include <grpcpp/impl/server_callback_handlers.h>
#include <grpcpp/server_context.h>
#include <grpcpp/impl/service_type.h>
#include <grpcpp/support/status.h>
#include <grpcpp/support/stub_options.h>
#include <grpcpp/support/sync_stream.h>

namespace gs {
namespace rpc {
namespace groot {

class GrootDdlService final {
 public:
  static constexpr char const* service_full_name() {
    return "gs.rpc.groot.GrootDdlService";
  }
  class StubInterface {
   public:
    virtual ~StubInterface() {}
    virtual ::grpc::Status batchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::gs::rpc::groot::BatchSubmitResponse* response) = 0;
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::BatchSubmitResponse>> AsyncbatchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::BatchSubmitResponse>>(AsyncbatchSubmitRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::BatchSubmitResponse>> PrepareAsyncbatchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::BatchSubmitResponse>>(PrepareAsyncbatchSubmitRaw(context, request, cq));
    }
    virtual ::grpc::Status getGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::gs::rpc::groot::GetGraphDefResponse* response) = 0;
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::GetGraphDefResponse>> AsyncgetGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::GetGraphDefResponse>>(AsyncgetGraphDefRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::GetGraphDefResponse>> PrepareAsyncgetGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::GetGraphDefResponse>>(PrepareAsyncgetGraphDefRaw(context, request, cq));
    }
    class async_interface {
     public:
      virtual ~async_interface() {}
      virtual void batchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest* request, ::gs::rpc::groot::BatchSubmitResponse* response, std::function<void(::grpc::Status)>) = 0;
      virtual void batchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest* request, ::gs::rpc::groot::BatchSubmitResponse* response, ::grpc::ClientUnaryReactor* reactor) = 0;
      virtual void getGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest* request, ::gs::rpc::groot::GetGraphDefResponse* response, std::function<void(::grpc::Status)>) = 0;
      virtual void getGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest* request, ::gs::rpc::groot::GetGraphDefResponse* response, ::grpc::ClientUnaryReactor* reactor) = 0;
    };
    typedef class async_interface experimental_async_interface;
    virtual class async_interface* async() { return nullptr; }
    class async_interface* experimental_async() { return async(); }
   private:
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::BatchSubmitResponse>* AsyncbatchSubmitRaw(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::grpc::CompletionQueue* cq) = 0;
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::BatchSubmitResponse>* PrepareAsyncbatchSubmitRaw(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::grpc::CompletionQueue* cq) = 0;
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::GetGraphDefResponse>* AsyncgetGraphDefRaw(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::grpc::CompletionQueue* cq) = 0;
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::gs::rpc::groot::GetGraphDefResponse>* PrepareAsyncgetGraphDefRaw(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::grpc::CompletionQueue* cq) = 0;
  };
  class Stub final : public StubInterface {
   public:
    Stub(const std::shared_ptr< ::grpc::ChannelInterface>& channel, const ::grpc::StubOptions& options = ::grpc::StubOptions());
    ::grpc::Status batchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::gs::rpc::groot::BatchSubmitResponse* response) override;
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::BatchSubmitResponse>> AsyncbatchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::BatchSubmitResponse>>(AsyncbatchSubmitRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::BatchSubmitResponse>> PrepareAsyncbatchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::BatchSubmitResponse>>(PrepareAsyncbatchSubmitRaw(context, request, cq));
    }
    ::grpc::Status getGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::gs::rpc::groot::GetGraphDefResponse* response) override;
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::GetGraphDefResponse>> AsyncgetGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::GetGraphDefResponse>>(AsyncgetGraphDefRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::GetGraphDefResponse>> PrepareAsyncgetGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::GetGraphDefResponse>>(PrepareAsyncgetGraphDefRaw(context, request, cq));
    }
    class async final :
      public StubInterface::async_interface {
     public:
      void batchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest* request, ::gs::rpc::groot::BatchSubmitResponse* response, std::function<void(::grpc::Status)>) override;
      void batchSubmit(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest* request, ::gs::rpc::groot::BatchSubmitResponse* response, ::grpc::ClientUnaryReactor* reactor) override;
      void getGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest* request, ::gs::rpc::groot::GetGraphDefResponse* response, std::function<void(::grpc::Status)>) override;
      void getGraphDef(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest* request, ::gs::rpc::groot::GetGraphDefResponse* response, ::grpc::ClientUnaryReactor* reactor) override;
     private:
      friend class Stub;
      explicit async(Stub* stub): stub_(stub) { }
      Stub* stub() { return stub_; }
      Stub* stub_;
    };
    class async* async() override { return &async_stub_; }

   private:
    std::shared_ptr< ::grpc::ChannelInterface> channel_;
    class async async_stub_{this};
    ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::BatchSubmitResponse>* AsyncbatchSubmitRaw(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::grpc::CompletionQueue* cq) override;
    ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::BatchSubmitResponse>* PrepareAsyncbatchSubmitRaw(::grpc::ClientContext* context, const ::gs::rpc::groot::BatchSubmitRequest& request, ::grpc::CompletionQueue* cq) override;
    ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::GetGraphDefResponse>* AsyncgetGraphDefRaw(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::grpc::CompletionQueue* cq) override;
    ::grpc::ClientAsyncResponseReader< ::gs::rpc::groot::GetGraphDefResponse>* PrepareAsyncgetGraphDefRaw(::grpc::ClientContext* context, const ::gs::rpc::groot::GetGraphDefRequest& request, ::grpc::CompletionQueue* cq) override;
    const ::grpc::internal::RpcMethod rpcmethod_batchSubmit_;
    const ::grpc::internal::RpcMethod rpcmethod_getGraphDef_;
  };
  static std::unique_ptr<Stub> NewStub(const std::shared_ptr< ::grpc::ChannelInterface>& channel, const ::grpc::StubOptions& options = ::grpc::StubOptions());

  class Service : public ::grpc::Service {
   public:
    Service();
    virtual ~Service();
    virtual ::grpc::Status batchSubmit(::grpc::ServerContext* context, const ::gs::rpc::groot::BatchSubmitRequest* request, ::gs::rpc::groot::BatchSubmitResponse* response);
    virtual ::grpc::Status getGraphDef(::grpc::ServerContext* context, const ::gs::rpc::groot::GetGraphDefRequest* request, ::gs::rpc::groot::GetGraphDefResponse* response);
  };
  template <class BaseClass>
  class WithAsyncMethod_batchSubmit : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithAsyncMethod_batchSubmit() {
      ::grpc::Service::MarkMethodAsync(0);
    }
    ~WithAsyncMethod_batchSubmit() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status batchSubmit(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::BatchSubmitRequest* /*request*/, ::gs::rpc::groot::BatchSubmitResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestbatchSubmit(::grpc::ServerContext* context, ::gs::rpc::groot::BatchSubmitRequest* request, ::grpc::ServerAsyncResponseWriter< ::gs::rpc::groot::BatchSubmitResponse>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(0, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  template <class BaseClass>
  class WithAsyncMethod_getGraphDef : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithAsyncMethod_getGraphDef() {
      ::grpc::Service::MarkMethodAsync(1);
    }
    ~WithAsyncMethod_getGraphDef() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status getGraphDef(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::GetGraphDefRequest* /*request*/, ::gs::rpc::groot::GetGraphDefResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestgetGraphDef(::grpc::ServerContext* context, ::gs::rpc::groot::GetGraphDefRequest* request, ::grpc::ServerAsyncResponseWriter< ::gs::rpc::groot::GetGraphDefResponse>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(1, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  typedef WithAsyncMethod_batchSubmit<WithAsyncMethod_getGraphDef<Service > > AsyncService;
  template <class BaseClass>
  class WithCallbackMethod_batchSubmit : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithCallbackMethod_batchSubmit() {
      ::grpc::Service::MarkMethodCallback(0,
          new ::grpc::internal::CallbackUnaryHandler< ::gs::rpc::groot::BatchSubmitRequest, ::gs::rpc::groot::BatchSubmitResponse>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::gs::rpc::groot::BatchSubmitRequest* request, ::gs::rpc::groot::BatchSubmitResponse* response) { return this->batchSubmit(context, request, response); }));}
    void SetMessageAllocatorFor_batchSubmit(
        ::grpc::MessageAllocator< ::gs::rpc::groot::BatchSubmitRequest, ::gs::rpc::groot::BatchSubmitResponse>* allocator) {
      ::grpc::internal::MethodHandler* const handler = ::grpc::Service::GetHandler(0);
      static_cast<::grpc::internal::CallbackUnaryHandler< ::gs::rpc::groot::BatchSubmitRequest, ::gs::rpc::groot::BatchSubmitResponse>*>(handler)
              ->SetMessageAllocator(allocator);
    }
    ~WithCallbackMethod_batchSubmit() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status batchSubmit(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::BatchSubmitRequest* /*request*/, ::gs::rpc::groot::BatchSubmitResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* batchSubmit(
      ::grpc::CallbackServerContext* /*context*/, const ::gs::rpc::groot::BatchSubmitRequest* /*request*/, ::gs::rpc::groot::BatchSubmitResponse* /*response*/)  { return nullptr; }
  };
  template <class BaseClass>
  class WithCallbackMethod_getGraphDef : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithCallbackMethod_getGraphDef() {
      ::grpc::Service::MarkMethodCallback(1,
          new ::grpc::internal::CallbackUnaryHandler< ::gs::rpc::groot::GetGraphDefRequest, ::gs::rpc::groot::GetGraphDefResponse>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::gs::rpc::groot::GetGraphDefRequest* request, ::gs::rpc::groot::GetGraphDefResponse* response) { return this->getGraphDef(context, request, response); }));}
    void SetMessageAllocatorFor_getGraphDef(
        ::grpc::MessageAllocator< ::gs::rpc::groot::GetGraphDefRequest, ::gs::rpc::groot::GetGraphDefResponse>* allocator) {
      ::grpc::internal::MethodHandler* const handler = ::grpc::Service::GetHandler(1);
      static_cast<::grpc::internal::CallbackUnaryHandler< ::gs::rpc::groot::GetGraphDefRequest, ::gs::rpc::groot::GetGraphDefResponse>*>(handler)
              ->SetMessageAllocator(allocator);
    }
    ~WithCallbackMethod_getGraphDef() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status getGraphDef(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::GetGraphDefRequest* /*request*/, ::gs::rpc::groot::GetGraphDefResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* getGraphDef(
      ::grpc::CallbackServerContext* /*context*/, const ::gs::rpc::groot::GetGraphDefRequest* /*request*/, ::gs::rpc::groot::GetGraphDefResponse* /*response*/)  { return nullptr; }
  };
  typedef WithCallbackMethod_batchSubmit<WithCallbackMethod_getGraphDef<Service > > CallbackService;
  typedef CallbackService ExperimentalCallbackService;
  template <class BaseClass>
  class WithGenericMethod_batchSubmit : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithGenericMethod_batchSubmit() {
      ::grpc::Service::MarkMethodGeneric(0);
    }
    ~WithGenericMethod_batchSubmit() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status batchSubmit(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::BatchSubmitRequest* /*request*/, ::gs::rpc::groot::BatchSubmitResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
  };
  template <class BaseClass>
  class WithGenericMethod_getGraphDef : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithGenericMethod_getGraphDef() {
      ::grpc::Service::MarkMethodGeneric(1);
    }
    ~WithGenericMethod_getGraphDef() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status getGraphDef(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::GetGraphDefRequest* /*request*/, ::gs::rpc::groot::GetGraphDefResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
  };
  template <class BaseClass>
  class WithRawMethod_batchSubmit : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawMethod_batchSubmit() {
      ::grpc::Service::MarkMethodRaw(0);
    }
    ~WithRawMethod_batchSubmit() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status batchSubmit(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::BatchSubmitRequest* /*request*/, ::gs::rpc::groot::BatchSubmitResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestbatchSubmit(::grpc::ServerContext* context, ::grpc::ByteBuffer* request, ::grpc::ServerAsyncResponseWriter< ::grpc::ByteBuffer>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(0, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  template <class BaseClass>
  class WithRawMethod_getGraphDef : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawMethod_getGraphDef() {
      ::grpc::Service::MarkMethodRaw(1);
    }
    ~WithRawMethod_getGraphDef() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status getGraphDef(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::GetGraphDefRequest* /*request*/, ::gs::rpc::groot::GetGraphDefResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestgetGraphDef(::grpc::ServerContext* context, ::grpc::ByteBuffer* request, ::grpc::ServerAsyncResponseWriter< ::grpc::ByteBuffer>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(1, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  template <class BaseClass>
  class WithRawCallbackMethod_batchSubmit : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawCallbackMethod_batchSubmit() {
      ::grpc::Service::MarkMethodRawCallback(0,
          new ::grpc::internal::CallbackUnaryHandler< ::grpc::ByteBuffer, ::grpc::ByteBuffer>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::grpc::ByteBuffer* request, ::grpc::ByteBuffer* response) { return this->batchSubmit(context, request, response); }));
    }
    ~WithRawCallbackMethod_batchSubmit() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status batchSubmit(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::BatchSubmitRequest* /*request*/, ::gs::rpc::groot::BatchSubmitResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* batchSubmit(
      ::grpc::CallbackServerContext* /*context*/, const ::grpc::ByteBuffer* /*request*/, ::grpc::ByteBuffer* /*response*/)  { return nullptr; }
  };
  template <class BaseClass>
  class WithRawCallbackMethod_getGraphDef : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawCallbackMethod_getGraphDef() {
      ::grpc::Service::MarkMethodRawCallback(1,
          new ::grpc::internal::CallbackUnaryHandler< ::grpc::ByteBuffer, ::grpc::ByteBuffer>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::grpc::ByteBuffer* request, ::grpc::ByteBuffer* response) { return this->getGraphDef(context, request, response); }));
    }
    ~WithRawCallbackMethod_getGraphDef() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status getGraphDef(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::GetGraphDefRequest* /*request*/, ::gs::rpc::groot::GetGraphDefResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* getGraphDef(
      ::grpc::CallbackServerContext* /*context*/, const ::grpc::ByteBuffer* /*request*/, ::grpc::ByteBuffer* /*response*/)  { return nullptr; }
  };
  template <class BaseClass>
  class WithStreamedUnaryMethod_batchSubmit : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithStreamedUnaryMethod_batchSubmit() {
      ::grpc::Service::MarkMethodStreamed(0,
        new ::grpc::internal::StreamedUnaryHandler<
          ::gs::rpc::groot::BatchSubmitRequest, ::gs::rpc::groot::BatchSubmitResponse>(
            [this](::grpc::ServerContext* context,
                   ::grpc::ServerUnaryStreamer<
                     ::gs::rpc::groot::BatchSubmitRequest, ::gs::rpc::groot::BatchSubmitResponse>* streamer) {
                       return this->StreamedbatchSubmit(context,
                         streamer);
                  }));
    }
    ~WithStreamedUnaryMethod_batchSubmit() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable regular version of this method
    ::grpc::Status batchSubmit(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::BatchSubmitRequest* /*request*/, ::gs::rpc::groot::BatchSubmitResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    // replace default version of method with streamed unary
    virtual ::grpc::Status StreamedbatchSubmit(::grpc::ServerContext* context, ::grpc::ServerUnaryStreamer< ::gs::rpc::groot::BatchSubmitRequest,::gs::rpc::groot::BatchSubmitResponse>* server_unary_streamer) = 0;
  };
  template <class BaseClass>
  class WithStreamedUnaryMethod_getGraphDef : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithStreamedUnaryMethod_getGraphDef() {
      ::grpc::Service::MarkMethodStreamed(1,
        new ::grpc::internal::StreamedUnaryHandler<
          ::gs::rpc::groot::GetGraphDefRequest, ::gs::rpc::groot::GetGraphDefResponse>(
            [this](::grpc::ServerContext* context,
                   ::grpc::ServerUnaryStreamer<
                     ::gs::rpc::groot::GetGraphDefRequest, ::gs::rpc::groot::GetGraphDefResponse>* streamer) {
                       return this->StreamedgetGraphDef(context,
                         streamer);
                  }));
    }
    ~WithStreamedUnaryMethod_getGraphDef() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable regular version of this method
    ::grpc::Status getGraphDef(::grpc::ServerContext* /*context*/, const ::gs::rpc::groot::GetGraphDefRequest* /*request*/, ::gs::rpc::groot::GetGraphDefResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    // replace default version of method with streamed unary
    virtual ::grpc::Status StreamedgetGraphDef(::grpc::ServerContext* context, ::grpc::ServerUnaryStreamer< ::gs::rpc::groot::GetGraphDefRequest,::gs::rpc::groot::GetGraphDefResponse>* server_unary_streamer) = 0;
  };
  typedef WithStreamedUnaryMethod_batchSubmit<WithStreamedUnaryMethod_getGraphDef<Service > > StreamedUnaryService;
  typedef Service SplitStreamedService;
  typedef WithStreamedUnaryMethod_batchSubmit<WithStreamedUnaryMethod_getGraphDef<Service > > StreamedService;
};

}  // namespace groot
}  // namespace rpc
}  // namespace gs


#endif  // GRPC_ddl_5fservice_2eproto__INCLUDED
