from cStringIO import StringIO

from string import strip

class PikConfigNode(object):
    def __init__(self, initValues = []):
        self._root = []
        self._root.extend(initValues)
    
    # Simple access to the data inside the node 
    def __getitem__(self, index):
        return self._root[index]
    
    def __setitem__(self, index, item):
        self._root[index] = item
    
    # Comment appears on the same line as the item,
    # prefixComment appears on the line above the comment.
    def append(self, item, comment = None, prefixComment = None):
        #if isinstance(item, PikConfigNode) and comment != None:
        #    raise RuntimeError("Comments not supported for ConfigNodes")
        
        self._root.append( (item, comment, prefixComment) )
    
    
    def __len__(self):
        return len(self._root)
    
    def __eq__(self, other):
        print "wat2", other, "wat"
        
        if not isinstance(other, PikConfigNode):
            return False
        elif len(self) != len(other):
            return False
        else:
            for item1, item2 in zip(self._root, 
                                    other._root):
                if item1 != item2:
                    return False
        
        return True
        
    
    # Add a node which is equal to a nested structure
    def addNode(self, initValues = [], comment = None, prefComment = None):
        node = PikConfigNode(initValues)
        self.append(node, comment, prefComment)
    
    # Add a single value, e.g. an integer
    def addValue(self, value, comment = None, prefComment = None):
        self.append(value, comment, prefComment)
    
    # Pikmin 2 config files contain items which start with some sort of identifier,
    # often followed by one or more values. 
    def addItem(self, identifier, *values, **kwargs):
        if "comment" in kwargs:
            comment = kwargs["comment"]
        else:
            comment = None
        
        if "prefComment" in kwargs:
            prefComment = kwargs["prefComment"]
        else:
            prefComment = None
        
        item = [identifier]
        item.extend(values)
        self.append(item, comment, prefComment)
    
    def __str__(self):
        string = StringIO()
        string.write("{\n")
        
        for item in self._root:
            data, comment, prev = item
            #print item, type(item), type(str(item))
            string.write(str(data))
            if comment != None:
                string.write(" # "+comment)
            string.write("\n")
        
        string.write("}")
        
        return string.getvalue()
    
    def _repr(self, identLevel):
        string = StringIO()
        ident = (identLevel*4)*" "
        
        for item in self._root:
            data, comment, prefComment = item
            if prefComment != None:
                for comm in prefComment:
                    string.write(ident+"# "+comm+"\n")
                    
            if isinstance(data, PikConfigNode):
                string.write(ident+"{")
                
                if comment != None:
                    string.write(" # "+comment)
                string.write("\n")
                
                string.write(data._repr(identLevel+1))
                string.write(ident+"}\n")
            elif isinstance(data, (list, tuple)):
                string.write(ident)
                string.write(" ".join(data))
                
                if comment != None:
                    string.write(" # " + comment)
               
                string.write("\n")
                
            else:
                string.write(ident)
                string.write(str(data))
                
                if comment != None:
                    string.write(" # " + comment)
                string.write("\n")
        
        return string.getvalue()

def load_pikconfig(fileobj):
    config = PikConfigNode()
    
    nested_nodes = []
    
    currentCommentBlock = []
    
    for line in fileobj:
        # We retrieve both the data and the comments, which are delimited by a #
        # To remove whitespace that doesn't have any use when working with data,
        # we will use strip on every string in the result of line.partition
        data, delimiter, comment = map(strip, line.partition("#"))
        
        # If there is no data, but there is a comment, this line is part of a comment block
        # and should be added to the current comment block.
        if len(data) == 0 and len(comment) > 0:
            currentCommentBlock.append(comment)
        
        
        if len(data) == 0:
            # There is no data to be parsed.
            continue
        elif len(comment) == 0:
            # There is no comment on this particular line.
            comment = None
        
        
        if data == "{":
            # The start of a new node
            node = PikConfigNode()
            
            # To support nested nodes, we add the new node to the nested nodes list.
            # When a node has been entered, all further data will be added to the last node in the list
            # which equals the latest node that has been entered.
            nested_nodes.append( (node, comment, currentCommentBlock) )
        elif data == "}":
            # The end of the node
            node, nodeComment, commentBlock = nested_nodes.pop()
            config.append(node, nodeComment, commentBlock)
        else:
            # To avoid duplicate code, we choose the node to add data to
            # based on if we have any nested nodes or not. If we do have 
            # at least one nested node, we will choose the last one from the list.
            if len(nested_nodes) > 0:
                node = nested_nodes[-1][0] #[0] refers to the node object
            else:
                node = config
            
            # Values are delimited by whitespace
            values = data.split(" ")
            
            # 
            if len(values) > 1:
                valueid = values[0]
                node.addItem(valueid, comment = comment, prefComment = currentCommentBlock, 
                             *values[1:])
            else:
                node.addValue(values[0], comment, currentCommentBlock)
            
            
        currentCommentBlock = []
    
    return config
        
        
        

def save_pikconfig(fileobj, pikconfig):
    fileobj.write(pikconfig._repr(0))



if __name__ == "__main__":
    with open("testfile.txt", "r") as f:
        config = load_pikconfig(f)
        
        print config
    
    with open("output.txt", "w") as f:
        save_pikconfig(f, config)
    
    with open("output.txt", "r") as f:
        config2 = load_pikconfig(f)
    
    
    print config == config2 # Should be a success!
    
            