class QR_manager:
    def __init__(self):
        self.qr_codes = {}

    def add_qr_code(self, code_id, data):
        self.qr_codes[code_id] = data

    def get_qr_code(self, code_id):
        return self.qr_codes.get(code_id, None)

    def read_qr_code
