from sharetop.core.stock import get_stock_kline_data
from sharetop.core.prepare import BasicTop

token = "9ada862fa17ce574"

# d = get_stock_kline_data(token, "BK0882")

d = BasicTop(token)

h = d.common_exec_func("pig_to_index")

print(h)
