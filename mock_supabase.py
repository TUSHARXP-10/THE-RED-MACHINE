class MockSupabase:
    """Mock Supabase client for offline development"""
    
    def __init__(self):
        self.connected = False
        
    def table(self, table_name):
        return MockTable(table_name)
        
class MockTable:
    def __init__(self, name):
        self.name = name
        
    def insert(self, data):
        print(f"Mock DB: Would insert to {self.name}: {data}")
        return MockResponse()
        
    def select(self, *args):
        print(f"Mock DB: Would select from {self.name}")
        return MockResponse()
        
class MockResponse:
    def execute(self):
        return {"data": [], "error": None}