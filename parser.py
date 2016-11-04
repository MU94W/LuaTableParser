from __future__ import print_function

class Parser(object):
    def __init__(self,table_str):
        self.table_str = table_str
        self.len = len(table_str)
        self.table = []
        self.count = 0
        pass

    def parser(self,ptr):   # init call X.parser(0)
        pass

    def quoteExp(self,ptr):     # assumption: X.table_str[ptr] == "'" | '"'
        r_ptr = ptr + 1
        string = self.table_str
        match = string[ptr]
        while (string[r_ptr] != match):
            r_ptr += 1
            pass
        r_ptr += 1
        quote_exp = string[ptr:r_ptr]
        return quote_exp, r_ptr

    def nameExp(self,ptr):      # assumption: X.table_str[ptr] != {"[" | "]" | "'" | '"'}
        r_ptr = ptr
        string = self.table_str
        while (r_ptr < self.len and string[r_ptr] != " " and string[r_ptr] != "]" and string[r_ptr] != "}" and string[r_ptr] != ";"):
            r_ptr += 1
            pass
        name_exp = string[ptr:r_ptr]
        return name_exp, r_ptr

    def squareExp(self,ptr):    # assumption: X.table_str[ptr] == "["
        l_ptr = ptr + 1
        string = self.table_str
        while (string[l_ptr] == " "):
            l_ptr += 1
            pass
        if (string[l_ptr] == "'" or string[l_ptr] == '"'):
            exp, r_ptr = self.quoteExp(l_ptr)
            pass
        else:
            exp, r_ptr = self.nameExp(l_ptr)
            pass
        ptr = r_ptr
        while (string[ptr] == " "):
            ptr += 1
            pass
        if (string[ptr] == "]"):
            ptr += 1
            square_exp = "[" + exp + "]"
            return square_exp, ptr
            pass
        else:
            pass
        pass

    def getLeftExp(self):
        self.count += 1
        l_exp = "[" + "%d" % (self.count) + "]"
        return l_exp

    def fieldParse(self,ptr):   # assumption: X.table_str[l_ptr] != { ";" | "{" }
        l_ptr = ptr
        string = self.table_str
        while (l_ptr < self.len and (string[l_ptr] == " " or string[l_ptr] == "{" or string[l_ptr] == ";")):
            l_ptr += 1
            pass
        if (l_ptr == self.len or string[l_ptr] == "}"):
            return "", self.len

        if (string[l_ptr] == "["):
            l_exp, lr_ptr = self.squareExp(l_ptr)
            rl_ptr = lr_ptr
            while (string[rl_ptr] == " " or string[rl_ptr] == "="):
                rl_ptr += 1
                pass
            if (string[rl_ptr] == "'" or string[rl_ptr] == '"'):
                r_exp, rr_ptr = self.quoteExp(rl_ptr)
                pass
            else:
                r_exp, rr_ptr = self.nameExp(rl_ptr)
                pass
            # print(l_exp,r_exp)
        elif (string[l_ptr] == "'" or string[l_ptr] == '"'):
            r_exp, rr_ptr = self.quoteExp(l_ptr)
            l_exp = self.getLeftExp()
        else:
            l_exp, lr_ptr = self.nameExp(l_ptr)
            equal_ptr = lr_ptr
            while (equal_ptr < self.len and string[equal_ptr] != ";" and string[equal_ptr] != "="):
                equal_ptr += 1
                pass
            if (equal_ptr == self.len or string[equal_ptr] == ";"):
                r_exp, rr_ptr = l_exp, lr_ptr
                l_exp = self.getLeftExp()
            else:
                l_exp = "." + l_exp
                rl_ptr = equal_ptr + 1
                while (string[rl_ptr] == " "):
                    rl_ptr += 1
                    pass
                if (string[rl_ptr] == "'" or string[rl_ptr] == '"'):
                    r_exp, rr_ptr = self.quoteExp(rl_ptr)
                    pass
                else:
                    r_exp, rr_ptr = self.nameExp(rl_ptr)
                    pass
            pass
        field = l_exp + " = " + r_exp
        while (rr_ptr < self.len and string[rr_ptr] != ";" and string[rr_ptr] != "}"):
            rr_ptr += 1
            pass
        return field, rr_ptr    # string[rr_ptr] == { ";" | "}" }

    def fieldlistParse(self,ptr,prefix):   # assumption: X.table_str[ptr] == "{"
        string = self.table_str
        next_field, next_ptr = self.fieldParse(ptr)
        if (next_field != ""):
            next_field = prefix + next_field
            self.table.append(next_field)
        while (next_ptr < self.len and string[next_ptr] != "}"):
            next_field, next_ptr = self.fieldParse(next_ptr)
            if (next_field != ""):
                next_field = prefix + next_field
                self.table.append(next_field)
            pass
        pass

    def tableConstructor(self):
        self.table = []
        table_name, rl_ptr = self.nameExp(0)
        local_table = "t"
        string = self.table_str
        while (rl_ptr < self.len and (string[rl_ptr] == " " or string[rl_ptr] == "=")):
            rl_ptr += 1
            pass
        self.table.append("do")
        self.table.append("local %s = {}" % (local_table))
        self.fieldlistParse(rl_ptr, local_table)
        self.table.append("%s = %s" % (table_name, local_table))
        self.table.append("end")
        pass
