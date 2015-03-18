#!/usr/bin/python
# -*- coding:utf-8 -*-
#import binascii
class Check_Words_Genegator():
    """
    Check_Words_Genegator class
    """
    my_bolean = (-4271564, 10675495)
    #asacem = (1926481717, 1498345613)
    asacem = (12970357, 12239417)
    sita = (12184167, 11429372)
    beta = (10237941, 6875192)
    SACEM_signature = ([10593052
                        , 10793079, 10793079, 10793079, 10793079, 10793079, 10793079, 10793079, 10793079
                        , 10793079, 10793079, 10793079, 10793079, 10793079, 10793079, 10793079, 10793079
                        , 11264795]
                        , [327487
                        , 8472041, 8472041, 8472041, 8472041, 8472041, 8472041, 8472041, 8472041
                        , 8472041, 8472041, 8472041, 8472041, 8472041, 8472041, 8472041, 8472041
                        , 1809675])
    myc = [[], []]

    sita_mod = [[847278254, 364407180, 1595608778, 474854131, 592516756, 1492835157, 1678212441, 1493712460, 1579677509, 1077013875, 1462968973, 1632567907, 1385664149, 1923144054, 1096620614L, 1170853586, 12184167, 1]
                , [876457445, 177827553, 468878045, 1353896545, 768682247, 724858619, 857984040, 626347674, 1430259357, 777071877, 494784776, 880682909, 916474133, 1078969273, 331143886, 278736205, 11429372, 1]]
    check_sum = [0, 0]
    
    def __init__(self):
        "checkwords init"
        #print '>>> __init__'
    
    def generate_num_c(self, _x, _index, _sub_in):
        #print '>>> generate_num_c'
        #print _x
        _temp = (-1 * (1 << 64)) % self.asacem[_index]
        _temp = (_temp * _x) % self.asacem[_index]
        return (_temp + self.SACEM_signature[_index][_sub_in]) % self.asacem[_index]
        
    def generate_bolean_normal(self, _x, _index, _sub_in):
        #print '>>> generate_bolean_normal'
        _x = self.my_bolean[_x]
        _temp = (-1 * (1 << 64)) % self.asacem[_index]
        _temp = (_temp * _x) % self.asacem[_index]
        return (_temp + self.SACEM_signature[_index][_sub_in]) % self.asacem[_index]

    def generate_bolean_c(self, _x, _index, _sub_in):
        #print '>>> generate_bolean_c'
        _sig = self.SACEM_signature[_index][_sub_in]
        _a = self.asacem[_index]
        _v = self.my_bolean[_x] % _a
        _beta = self.beta[_index]
        _c1_64 = (1 << 64) % _a         #_c1_64 = 1106004
        _i = _sub_in
        return (_sig - ((_c1_64 * _v) % _a) - ((_c1_64 * _beta * _i) % _a)) % _a
    
    def generate_cx(self, _varx):
        self.myc = [[], []]
        for i in range(0, len(_varx)):
            if i == 0 or (_varx[i] != 1 and _varx[i] != 0):
                _ci_1 = self.generate_num_c(_varx[i], 0, i)
                _ci_2 = self.generate_num_c(_varx[i], 1, i)
            elif  i == 17:  
                _ci_1 = self.generate_bolean_normal(_varx[i], 0, i)
                _ci_2 = self.generate_bolean_normal(_varx[i], 1, i)
            else:
                _ci_1 = self.generate_bolean_c(_varx[i], 0, i)
                _ci_2 = self.generate_bolean_c(_varx[i], 1, i)
            self.myc[0].append(_ci_1)
            self.myc[1].append(_ci_2)
        #print self.myc
    
    def generate_s(self, _index):
        #print '>>> generate_s'
        _sum = self.myc[_index][0] % self.asacem[_index]
        #print _sum
        for i in range(1, 18):
            #print i
            _sum = (self.sita[_index] * _sum + self.myc[_index][i]) % self.asacem[_index]
            #_temp = (self.sita_mod[_index][i] % self.asacem[_index])
            #_sum = (_sum + _temp * self.myc[_index][i]) % self.asacem[_index]
            #print _sum
        return _sum
    
    def reverse(self, _temp):
        #print '>>> reverse'

        _list = []
        while _temp / 2 != 0:
            _list.append(_temp % 2)
            _temp = _temp / 2
        _list.append(_temp % 2)
        while len(_list) < 32:
            _list.append(0)

        _res = 0
        for item in _list:
            _res = _res * 2 + item
        return _res
    
    #generate_check_words
    #varx [beacon_id BM-0...BM-15 default_message]
    def generate_check_words(self, varx):
        self.generate_cx(varx)
        
        self.check_sum[0] = self.generate_s(0)
        self.check_sum[1] = self.generate_s(1)
        _s1 = (self.check_sum[0] * self.sita[0]) % self.asacem[0]
        _s2 = (self.check_sum[1] * self.sita[1]) % self.asacem[1]
        _res_s1 = self.reverse(_s1)
        _res_s2 = self.reverse(_s2)
        #print '========================'
        #print self.check_sum
        #print _s1, _s2, _res_s1, _res_s2
        #print hex(_res_s1)
        #print hex(_res_s2)

        #print self.GetReadableFrame(_s1)
        #print self.GetReadableFrame(_s2)
        #print self.GetReadableFrame(_res_s1)
        #print self.GetReadableFrame(_res_s2)
        return (_res_s1, _res_s2)
        #return str(self.GetReadableFrame(_res_s1)), str(self.GetReadableFrame(_res_s2))
        
    def GetReadableFrame(self, data):        
        result = []
        res = ''
        while data / 16 != 0:
            tempint = data % 16
            data = data / 16
            result.append(hex(tempint)[2:3])
        tempint = data % 16
        result.append(hex(tempint)[2:3])
        for item in reversed(result):
            res += item
        return res

if __name__ == '__main__':
    #sys.setdefaultencoding('utf-8')  
    window = Check_Words_Genegator()
    _ss1, _ss2 = window.generate_check_words([2127, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0])
