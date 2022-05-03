# QR code-learning

## 介绍

本来我自己用来学习二维码原理的代码，但在学习过程中我发现中文互联网对二维码原理方面的资料并不是很多，其中大部分只是介绍二维码的规格和基本常识，没有深入介绍其底层原理，所以我希望能写一些东西来帮助有需要的人

## 示例

```python
from QRcodev2 import QRcode
a = QRcode("HELLO WORLD",0,2) # QRcode(str,version,level) 
a.make()
```

默认version = 0 (自动选择适合的version) level = 1(M)

## 教程

1. 分析你要编码的数据，选择编码模式
2. 编码数据
3. 生成纠错码
4. 构建最终数据
5. 填充二维码
6. 掩码
7. 填充格式和版本信息

## Contributing

本人水平有限，还请海涵，也欢迎大家提出issue和pull request 

---

参考资料：

 	1. https://www.thonky.com/qr-code-tutorial/
 	2. https://coolshell.cn/articles/10590.html

