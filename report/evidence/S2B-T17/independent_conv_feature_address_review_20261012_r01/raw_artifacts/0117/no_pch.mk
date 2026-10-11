# 关闭可重建PCH，仅保留同一C++来源和普通编译参数。
%.o: %.cpp
	$(CXX) $(OPT_FAST) $(CXXFLAGS) $(CPPFLAGS) -c -o $@ $<
