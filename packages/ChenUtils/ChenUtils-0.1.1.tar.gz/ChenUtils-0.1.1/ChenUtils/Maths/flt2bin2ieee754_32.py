def flt2bin(flt: float) -> str:
    """
    浮点数转二进制小数
    :param flt: 待转换的浮点数
    :return: 转换后的二进制小数的字符串
    """
    # 全部按正数来算
    is_neg = False
    if flt < 0:
        is_neg = True
        flt = -flt

    # 处理整数部分
    int_part = int(flt)
    dec_part = flt - int_part
    int_bin = bin(int_part)[2:]

    # 处理小数部分
    dec_bin = ""
    while dec_part > 0:
        dec_part *= 2
        bit = int(dec_part)
        dec_bin += str(bit)
        dec_part -= bit

    # 如果有1.0这种小数为0时，不会进入上面的循环，需要补上一个0
    if not len(dec_bin):
        dec_bin = '0'

    binary = int_bin + "." + dec_bin
    if is_neg:
        binary = '-' + binary
    return binary + 'B'


def bin2flt(binary: str) -> float:
    """
    二进制小数转浮点数
    :param binary: 待转换的二进制小数的字符串
    :return: 转换后的浮点数
    """
    int_bin, dec_bin = binary[:-1].split('.')

    # 按正数来计算
    is_neg = False
    if '-' in int_bin:
        is_neg = True
        int_bin = int_bin[1:]

    # 整数部分直接转换
    int_part = int(int_bin, 2)

    # 处理小数部分
    dec_part = 0.0
    idx = -1
    for i in range(len(dec_bin)):
        if dec_bin[i] == '1':
            dec_part += (2 ** idx)
        idx -= 1

    flt = float(int_part) + dec_part
    if is_neg:
        flt = -flt
    return flt


def flt2ieee754(flt: float) -> str:
    """
    浮点数转ieee754规格化表示
    :param flt: 待转换的浮点数
    :return: 转换后的ieee754规格化表示的字符串
    """
    # 符号位
    is_neg = '0'
    if flt < 0:
        flt = -flt
        is_neg = '1'

    binary = flt2bin(flt)
    front, back = binary.split('.')
    # 去除末尾的B
    back = back[:-1]

    if front != '0':
        # 阶码
        idx = len(front) - 1
        # 补全到8位
        e = idx + 127
        order_code = bin(e)[2:].rjust(8, '0')
        ans = is_neg + order_code + front[1:] + back
        ans = ans.ljust(32, '0')
        return hex(int(ans, 2))[2:].upper() + 'H'
    else:
        # 数字为0.xxx的情况，小数点要向后移动
        pos = back.find('1') + 1
        idx = -pos
        e = idx + 127
        order_code = bin(e)[2:].rjust(8, '0')
        ans = is_neg + order_code + back[pos:]
        ans = ans.ljust(32, '0')
        return hex(int(ans, 2))[2:].upper() + 'H'


def ieee7542bin(ieee754: str) -> str:
    """
    ieee754规格化表示转二进制小数
    :param ieee754: ieee754规格化表示的字符串
    :return: 转换后的二进制小数的字符串
    """
    # 转二进制会去掉前面的0，先补全为32位
    flt_bin = bin(int(ieee754[:-1], 16))[2:].rjust(32, '0')
    is_neg = False
    if flt_bin[0] == '1':
        is_neg = True

    # 小数点移动位数
    e = int(flt_bin[1:9], 2)
    idx = e - 127

    if idx >= 0:
        front = '1' + flt_bin[9:9 + idx]
        # 去掉后面补全的0
        back = flt_bin[9 + idx:].rstrip('0')
    else:
        # 是0.xxx的情况
        cnt = -idx
        front = '0'
        # 小数点后是0.(cnt-1个0)1(尾数)
        back = '0' * (cnt - 1) + '1' + flt_bin[9:].rstrip('0')
    binary = front + '.' + back
    if is_neg:
        binary = '-' + binary
    return binary + 'B'


def bin2ieee754(binary: str) -> str:
    """
    二进制小数转ieee754规格化表示
    :param binary: 待转换的二进制小数的字符串
    :return: 转换后的ieee754规格化表示的字符串
    """
    flt = bin2flt(binary)
    ieee754 = flt2ieee754(flt)
    return ieee754


def ieee7542flt(ieee754: str) -> float:
    """
    ieee754规格化表示转浮点数
    :param ieee754: 待转换的ieee754规格化表示的字符串
    :return: 转换后的浮点数
    """
    binary = ieee7542bin(ieee754)
    flt = bin2flt(binary)
    return flt


if __name__ == '__main__':
    # print(flt2bin(11.375))
    # print(flt2ieee754(11.375))
    # print(bin2flt('1011.011B'))
    # print(bin2ieee754('1011.011B'))
    # print(ieee7542flt('41360000H'))
    # print(ieee7542bin('41360000H'))
    # print()
    # print(flt2bin(-135.625))
    # print(flt2ieee754(-135.625))
    # print(bin2flt('-10000111.101B'))
    # print(bin2ieee754('-10000111.101B'))
    # print(ieee7542flt('C307A000H'))
    # print(ieee7542bin('C307A000H'))
    # print()
    # print(flt2bin(0.375))
    # print(flt2ieee754(0.375))
    # print(bin2flt('0.011B'))
    # print(bin2ieee754('0.011B'))
    # print(ieee7542flt('3EC00000H'))
    # print(ieee7542bin('3EC00000H'))
    # print()
    # print(flt2bin(-0.25))
    # print(flt2ieee754(-0.25))
    # print(bin2flt('-0.01B'))
    # print(bin2ieee754('-0.01B'))
    # print(ieee7542flt('BE800000H'))
    # print(ieee7542bin('BE800000H'))

    f = float(input())
    ie = flt2ieee754(f)
    print(ie)
    print(ieee7542flt(ie))
