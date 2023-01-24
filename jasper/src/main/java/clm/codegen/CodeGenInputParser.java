package clm.codegen;

import com.github.javaparser.Range;
import com.github.javaparser.ast.Node;

import clm.jasper.ContextParser;
import clm.jasper.Parser;

public class CodeGenInputParser {
    
    /**
     * Given the buggy file, the buggy line, and an input config, get the codegen input
     * 
     * @param filename the buggy file
     * @param startLine the start line of the buggy lines
     * @param endLine the endline of the buggy lines (included)
     * @param config a config in enum CodeT5Config
     * @return a CodeGenInput object
     */
    public static CodeGenInput getCodeGenInput(String filename, int startLine, int endLine, CodeGenConfig config) {
        try {
            Node buggyFunctionNode = ContextParser.getSurroundingFunctionNode(filename, startLine, endLine, true);
            Range range = buggyFunctionNode.getRange().get();
            String functionRange = range.begin.line + "," + range.begin.column + "-" + range.end.line + "," + range.end.column;
            String input = "";
            if (config == CodeGenConfig.CODEGEN_COMPLETE_CODEFORM_NOCOMMENT) {
                String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(filename, startLine, endLine, true);
                input = buggyFunctionBefore;
            } else if (config == CodeGenConfig.CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT) {
                String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(filename, startLine, endLine, true);
                String buggyLine = ContextParser.getDedentedCode(filename, startLine, endLine, true);
                input = buggyFunctionBefore;
                for (String line : buggyLine.split("\\n")) {
                    if (line.trim().equals(""))
                        continue;
                    input += "\n// buggy line:" + line;
                }
            }
            input = Parser.removeEmptyLines(input);
            return new CodeGenInput(input, functionRange);
        } catch (Exception e){
            System.out.println(e);
            return new CodeGenInput("", "");
        }
    }

    /**
     * Dump the codetgen result into a json file
     * 
     * @param filename the buggy file
     * @param startLine the start line of the buggy lines
     * @param endLine the endline of the buggy lines (included)
     * @param config a config in enum CodeGenConfig
     * @param outputFileName the json file to dump the codex input
     */
    public static void dumpCodeGenInput(String filename, int startLine, int endLine, CodeGenConfig config, String outputFileName) throws Exception {
        CodeGenInput codegenInput = getCodeGenInput(filename, startLine, endLine, config);
        codegenInput.dumpAsJson(outputFileName);
    }

    
    /** 
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {
        if (args.length == 5) {
            String filename = args[0];
            int startLine = Integer.parseInt(args[1]);
            int endLine = Integer.parseInt(args[2]);
            CodeGenConfig config = null;
            if (args[3].equals("CODEGEN_COMPLETE_CODEFORM_NOCOMMENT")){
                config = CodeGenConfig.CODEGEN_COMPLETE_CODEFORM_NOCOMMENT;
            } else if (args[3].equals("CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT")) {
                config = CodeGenConfig.CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT;
            } else {
                throw new Exception("Unrecognized CodeGenConfig: " + args[3]);
            }
            String outputFileName = args[4];
            dumpCodeGenInput(filename, startLine, endLine, config, outputFileName);
        } else {
            throw new Exception("Arguments number mismatched, expected 5, but got " + args.length);
        }
    }

}
