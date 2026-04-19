# Day 2 Notes

## 今天学习的内容
今天我学习了文本切分，也就是把长文本拆成多个小块，为后续检索做准备。

## 我对 chunk_size 的理解
chunk_size 表示每个文本块的大小。它越大，切出来的块越少；它越小，切出来的块越多。

## 我对 chunk_overlap 的理解
chunk_overlap 表示相邻文本块之间重复保留的内容。设置 overlap 可以减少上下文断裂的问题。

## 我的实验观察
- 当 chunk_size 变大时，chunk 数量减少
- 当 chunk_size 变小时，chunk 数量增加
- 当 overlap 增大时，相邻 chunk 内容重复更多

## 今天的收获
我开始理解 RAG 并不是直接把整篇文章拿来问，而是先把文章切成多个 chunk，后面再从这些 chunk 里检索最相关的内容。