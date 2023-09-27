from utils.log import logger


def registry_server_handler():
    """
    创建grpc服务器
    """
    import grpc
    from concurrent import futures
    from registry_config import RegistryConfig

    address = f"0.0.0.0:{RegistryConfig.server_port}"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=RegistryConfig.max_worker),
                         options=[("grpc.max_receive_message_length", 2147483647),
                                  ("grpc.max_send_message_length", 2147483647)])
    import registry_pb2_grpc
    from registry_service import RegistryService
    registry_pb2_grpc.add_RegistryServiceServicer_to_server(RegistryService(), server)
    server.add_insecure_port(address)
    server.start()
    logger.info(f"registry {address} server start success")

    server.wait_for_termination()
    return server
