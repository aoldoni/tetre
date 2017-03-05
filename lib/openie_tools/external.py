

class ExternalToolsPrepare():
    def __init__(self, args):
        self.args = args

    def run(self):
        for token_original, sentence in get_tokens(self.args):
            filename = self.args.word+"-"+str(sentence.file_id)+"-"+str(sentence.id)+"-"+str(token_original.idx)
            output_path = self.args.directory+output_comparison

            with open(output_path + filename, 'w') as output:
                output.write(str(sentence))

        return

class ExternalToolsRun():
    def __init__(self, args):
        self.args = args

    def run(self):
        interface = ExternalInterface(self.args)

        lst = os.listdir(self.args.directory+output_comparison)
        lst.sort()

        for fn in lst:

            if (fn == ".DS_Store"):
                continue

            if (not self.args.word in fn):
                continue

            file = self.args.directory + output_comparison + fn
            out = self.args.directory + interface.get_interface().dir + fn
            interface.run(file, out)


        return
