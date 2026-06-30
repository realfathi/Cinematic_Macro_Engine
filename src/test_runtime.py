import sys
sys.path.append('e:/Cinematic_Macro_Engine/src')
import database

df = database.get_runtime_paradox("All")
print("Columns:", df.columns.tolist())
