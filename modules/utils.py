import logging

def setup_logging():
    logging.basicConfig(
        filename='D:/Tools/PC Controller/pc_controller.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
