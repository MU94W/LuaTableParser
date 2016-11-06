from __future__ import print_function

fieldsep = (';',',',)
tablesep = ('{','}',)
square = ("[","]",)
quote = ("'",'"',)
blank = (' ',)
equal = ('=',)
prefixset = ('P','Q',)

class SimpleParser(object):
    def __init__(self,text):
        self.text = text + fieldsep[0]
        self.len = len(self.text)
        self.table = []
        self.count = 0

    def isInSet(self,char,someset):
        for item in someset:
            if (item == char):
                return True
        return False

    def countExp(self):
        self.count += 1
        return "[%d]" % (self.count)

    def quoteParse(self,ptr):
        txt = self.text
        l_ptr = ptr
        l_quote = txt[l_ptr]
        ptr += 1
        char = txt[ptr]
        while True:
            if (char == l_quote and txt[ptr-1] != "\\"):
                break
            ptr += 1
            if (ptr == self.len):
                pass
            char = txt[ptr]
        r_ptr = ptr + 1
        return l_ptr, r_ptr

    def expParse(self,ptr):
        txt = self.text
        l_ptr = ptr
        ptr += 1
        char = txt[ptr]
        sets = blank + (square[1],) + fieldsep + tablesep + equal
        while (not self.isInSet(char,sets)):
            ptr += 1
            if (ptr == self.len):
                pass
            char = txt[ptr]
        r_ptr = ptr
        return l_ptr, r_ptr

    def quoteAexpParse(self,ptr):
        txt = self.text
        char = txt[ptr]
        while (self.isInSet(char,blank)):
            ptr += 1
            if (ptr == self.len):
                pass
            char = txt[ptr]
        if (self.isInSet(char,quote)):
            l_ptr, r_ptr = self.quoteParse(ptr)
        else:
            l_ptr, r_ptr = self.expParse(ptr)
        return l_ptr, r_ptr

    def isChildTable(self,ptr):
        txt = self.text
        char = txt[ptr]
        while (self.isInSet(char,blank)):
            ptr += 1
            if (ptr == self.len):
                pass
            char = txt[ptr]
        if (self.isInSet(char,tablesep)):
            if (char == tablesep[0]):
                return True, ptr
            else:
                pass    # error handle
        else:
            return False, ptr

    def rightParse(self,ptr,prefixindex,l_exp):
        flag, ptr = self.isChildTable(ptr)
        txt = self.text
        endset = fieldsep + tablesep
        if flag:    # make child table
            newindex = 1 - prefixindex
            self.table.append("do")
            self.table.append("local %s = {}" % (prefixset[newindex]))
            tmp = SimpleParser(txt)       # Assumption: new object.text start with a tablesep
            ptr = tmp.fieldlistParse(ptr,newindex)      # txt[ptr] == "}"
            self.table += tmp.table
            r_exp = prefixset[newindex]
            self.table.append("%s = %s" % (l_exp,r_exp))
            self.table.append("end")
            ptr = self.expectSymbol(ptr+1,endset)
        else:
            l_ptr, r_ptr = self.quoteAexpParse(ptr)
            r_exp = txt[l_ptr:r_ptr]
            self.table.append("%s = %s" % (l_exp,r_exp))
            ptr = self.expectSymbol(r_ptr,endset)         # Assumption: each field endded with a fieldsep or tablesep
        return ptr

    def expectSymbol(self,ptr,symset,throw_error=True):
        txt = self.text
        char = txt[ptr]
        while (self.isInSet(char,blank)):
            ptr += 1
            if (ptr == self.len):
                pass
            char = txt[ptr]
        if (not self.isInSet(char,symset) and throw_error):
            pass
        return ptr

    def fieldParse(self,ptr,prefixindex):
        txt = self.text
        char = txt[ptr]
        sets = fieldsep + blank
        while (self.isInSet(char,sets)):
            ptr += 1
            if (ptr == self.len):
                pass
            char = txt[ptr]
        if (char == tablesep[1]):
            return ptr

        if (char == tablesep[0]):
            l_exp = prefixset[prefixindex] + self.countExp()
            ptr = self.rightParse(ptr,prefixindex,l_exp)
            return ptr 
        elif (char == square[0]):
            l_ptr, r_ptr = self.quoteAexpParse(ptr+1)
            l_exp = "%s[%s]" % (prefixset[prefixindex],txt[l_ptr:r_ptr])

            ptr = self.expectSymbol(r_ptr,square)
            ptr = self.expectSymbol(ptr+1,equal)

            ptr = self.rightParse(ptr+1,prefixindex,l_exp)
            return ptr
        else:
            l_ptr, r_ptr = self.quoteAexpParse(ptr)
            ptr = self.expectSymbol(r_ptr,equal,throw_error=False)
            if (not self.isInSet(txt[ptr],equal)):
                endset = fieldsep + tablesep
                if (self.isInSet(txt[ptr],endset)):            # Assumption: each field endded with a fieldsep or tablesep
                    r_exp = txt[l_ptr:r_ptr]
                    l_exp = prefixset[prefixindex] + self.countExp()
                    self.table.append("%s = %s" % (l_exp,r_exp))
                    return ptr
                else:
                    pass
            else:
                l_exp = '%s["%s"]' % (prefixset[prefixindex],txt[l_ptr:r_ptr])

                ptr = self.rightParse(ptr+1,prefixindex,l_exp)
                return ptr
    
    def fieldlistParse(self,ptr,prefixindex):
        self.table = []
        txt = self.text
        ptr = self.fieldParse(ptr+1,prefixindex)                # fieldParse doesn't pass the first "{"
        char = txt[ptr]
        while (self.isInSet(char,fieldsep)):
            ptr = self.fieldParse(ptr,prefixindex)
            char = txt[ptr]

        if (not self.isInSet(char,tablesep)):
            pass
        else:
            return ptr      # txt[ptr] == "}"

    def tableConstructor(self):
        self.table = []
        txt = self.text
        prefixindex = 0
        l_ptr, r_ptr = self.expParse(0)
        l_exp = txt[l_ptr:r_ptr]
        ptr = self.expectSymbol(r_ptr,equal)
        ptr = self.rightParse(ptr+1,prefixindex,l_exp)
        return True


