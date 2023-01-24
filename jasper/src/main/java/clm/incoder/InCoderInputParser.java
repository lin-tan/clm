package clm.incoder;

import com.github.javaparser.Range;
import com.github.javaparser.ast.Node;

import clm.jasper.ContextParser;
import clm.jasper.Parser;

public class InCoderInputParser {
    public static InCoderInput getInCoderInput(String filename, int startLine, int endLine, InCoderConfig config) {
        try {
            Node buggyFunctionNode = ContextParser.getSurroundingFunctionNode(filename, startLine, endLine, true);
            Range range = buggyFunctionNode.getRange().get();
            String functionRange = range.begin.line + "," + range.begin.column + "-" + range.end.line + "," + range.end.column;
            String input = "";
            if (config == InCoderConfig.INCODER_COMPLETE_CODEFORM_NOCOMMENT) {
                String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(filename, startLine, endLine, true);
                String buggyFunctionAfter = ContextParser.getSurroundingFunctionAfter(filename, startLine, endLine, true);
                int buggyLineIndent = Parser.getIndent(filename, startLine);
                int buggyFunctionIndent = Parser.getIndent(buggyFunctionNode);

                input = buggyFunctionBefore + "\n";
                for (int i = 0; i < buggyLineIndent - buggyFunctionIndent; i += 1)
                    input += " ";
                input += "<|mask:0|>\n" + buggyFunctionAfter;
            } else if (config == InCoderConfig.INCODER_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT) {
                String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(filename, startLine, endLine, true);
                String buggyFunctionAfter = ContextParser.getSurroundingFunctionAfter(filename, startLine, endLine, true);
                String buggyLine = ContextParser.getDedentedCode(filename, startLine, endLine, true);
                int buggyLineIndent = Parser.getIndent(filename, startLine);
                int buggyFunctionIndent = Parser.getIndent(buggyFunctionNode);

                input = buggyFunctionBefore;
                for (String line : buggyLine.split("\\n")) {
                    if (line.trim().equals(""))
                        continue;
                    input += "\n// buggy line:" + line;
                }
                input += "\n";
                for (int i = 0; i < buggyLineIndent - buggyFunctionIndent; i += 1)
                    input += " ";
                input += "<|mask:0|>\n" + buggyFunctionAfter;
            }
            input = Parser.removeEmptyLines(input) + "\n<|mask:0|>";
            return new InCoderInput(input, functionRange);
        } catch (Exception e){
            System.out.println(e);
            return new InCoderInput("", "");
        }
    }

    public static void dumpInCoderInput(String filename, int startLine, int endLine, InCoderConfig config, String outputFileName) throws Exception{
        InCoderInput codet5Input = getInCoderInput(filename, startLine, endLine, config);
        codet5Input.dumpAsJson(outputFileName);
    }

    public static void main(String[] args) throws Exception {
        if (args.length == 5) {
            String filename = args[0];
            int startLine = Integer.parseInt(args[1]);
            int endLine = Integer.parseInt(args[2]);
            InCoderConfig config = null;
            if (args[3].equals("INCODER_COMPLETE_CODEFORM_NOCOMMENT")) {
                config = InCoderConfig.INCODER_COMPLETE_CODEFORM_NOCOMMENT;
            } else if (args[3].equals("INCODER_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT")) {
                config = InCoderConfig.INCODER_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT;
            } else {
                throw new Exception("Unrecognized InCoderConfig: " + args[3]);
            }
            String outputFileName = args[4];
            dumpInCoderInput(filename, startLine, endLine, config, outputFileName);
        } else {
            throw new Exception("Arguments number mismatched, expected 5, but got " + args.length);
        }
    }
}
