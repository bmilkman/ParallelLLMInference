## Background

Currently, there are many large models available online, many of which offer multi-GPU parallel computing capabilities. However, these features are largely due to the insufficient VRAM of
single cards, so inference is performed through VRAM sharing. Large companies usually have a considerable reserve of enterprise GPUs, and hope to use large models to batch-process very large-scale tasks. 
In such scenarios, smaller models are clearly more favored, as single-card inference with small models is not an issue. The challenge lies in how to use multiple cards to accelerate
the inference speed. The main content of this repository includes a request dispatcher (server.py) and a concurrent solution for multiple backend large model APIs. The LLM API code is not
uploaded here, but those with similar needs can reuse this dispatcher to implement asynchronous parallel inference computing. The dispatcher includes examples of both asynchronous and
synchronous operations.



## 背景

目前网上有非常多的大模型，很多提供了多卡并行计算的功能，但这些功能更多是因为单卡的显存不足，所以通过显存共享的方式去做推理。
大公司一般都会有比较多的显卡储备，希望通过大模型去批量做一些规模非常大的事情。这种场景下明显小模型更受青睐，而单卡推理小模型并不是问题，问题在于如何通过使用多张卡去加速推理的速度。
此仓库主要内容为一个请求分发器（server.py)和N个后端大模型API的并发解决方案。在此并没有上传LLM API的代码，如果有相同需求的人可以复用这个分发器去实现异步并行推理的计算。
分发器里写了异步的例子和一个同步的例子。
