import formatter
import StringIO

class Paragraph:
    def __init__(self):
        self.text = ''
        self.bytes = 0
        self.density = 0.0
        
class LineWriter(formatter.AbstractWriter):
    def __init__(self, *args):
        self.last_index = 0
        self.lines = [Paragraph()]
        formatter.AbstractWriter.__init__(self)
        
    def send_flowing_data(self, data):
        # Work out the length of this data chunk
        data_length = len(data)

        # We have parsed more text, so increment index
        self.index += data_length

        # Calculate the number of bytes since last time
        data_bytes = self.index - self.last_index
        self.last_index = self.index
        
        # Accumulate this information in current line
        l = self.lines[-1]
        l.text += data
        l.bytes += data_bytes
        
    def send_paragraph(self, blankline):
        """ Create a new paragraph if necessary """
        if self.lines[-1].text == '':
            return
        
        self.lines[-1].text += '\n' * (blankline + 1)
        self.lines[-1].bytes += 2 * (blankline + 1)
        self.lines.append(Paragraph())
        
    def send_literal_data(self, data):
        self.send_flowing_data(data)
        
    def send_line_break(self):
        self.send_paragraph(0)
        
    def compute_density(self):
        """Calculate the density for each line, and the average."""
        total = 0.0
        for l in self.lines:
            l.density = len(l.text) / float(l.bytes)
            total += l.density
        # Store for optional use by the neural network.
        self.average = total / float(len(self.lines))        
        
    def output(self):
        """Return a string with the useless lines filtered out."""
        self.compute_density()
        output = StringIO.StringIO()
        for l in self.lines:
            # Check density against threshold.
            # Custom filter extensions go here.
            if l.density > 0.5:
	        output.write(l.text)
        return output.getvalue()
        
    