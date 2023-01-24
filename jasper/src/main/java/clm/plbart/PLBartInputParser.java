package clm.plbart;

import com.github.javaparser.Range;
import com.github.javaparser.ast.Node;

import clm.jasper.ContextParser;
import clm.jasper.Parser;

public class PLBartInputParser {
    /**
     * Given the buggy file, the buggy line, and an input config, get the PLBart input
     * 
     * @param filename the buggy file
     * @param startLine the start line of the buggy lines
     * @param endLine the endline of the buggy lines (included)
     * @param config a config in enum PLBartConfig
     * @return a PLBartInput object
     */
    public static PLBartInput getPLBartInput(String filename, int startLine, int endLine, PLBartConfig config) {
        try {
            Node buggyFunctionNode = ContextParser.getSurroundingFunctionNode(filename, startLine, endLine, true);
            Range range = buggyFunctionNode.getRange().get();
            String functionRange = range.begin.line + "," + range.begin.column + "-" + range.end.line + "," + range.end.column;
            String input = "";
            if (config == PLBartConfig.PLBART_SEQFORM_MASKFORM_NOCOMMENT) {
                String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(filename, startLine, endLine, true);
                String buggyFunctionAfter = ContextParser.getSurroundingFunctionAfter(filename, startLine, endLine, true);
                int buggyLineIndent = Parser.getIndent(filename, startLine);
                int buggyFunctionIndent = Parser.getIndent(buggyFunctionNode);

                input = buggyFunctionBefore + "\n";
                // add the idnentation
                for (int i = 0; i < buggyLineIndent - buggyFunctionIndent; i += 1)
                    input += " ";
                input += "<mask>\n" + buggyFunctionAfter;
            } else if (config == PLBartConfig.PLBART_SEQFORM_COMMENTFORM_NOCOMMENT) {
                String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(filename, startLine, endLine, true);
                String buggyFunctionAfter = ContextParser.getSurroundingFunctionAfter(filename, startLine, endLine, true);
                String buggyLine = ContextParser.getDedentedCode(filename, startLine, endLine, true);
                int buggyLineIndent = Parser.getIndent(filename, startLine);
                int buggyFunctionIndent = Parser.getIndent(buggyFunctionNode);

                input = buggyFunctionBefore;
                input += "\n/* buggy line: " + buggyLine.substring(0, buggyLine.length() - 1) + " */\n";
                // add the idnentation
                for (int i = 0; i < buggyLineIndent - buggyFunctionIndent; i += 1)
                    input += " ";
                input += "<mask>\n" + buggyFunctionAfter;
            }
            input = Parser.removeEmptyLines(input);
            return new PLBartInput(input, functionRange);
        } catch (Exception e){
            System.out.println(e);
            return new PLBartInput("", "");
        }
    }

    /**
     * Dump the plbart result into a json file
     * 
     * @param filename the buggy file
     * @param startLine the start line of the buggy lines
     * @param endLine the endline of the buggy lines (included)
     * @param config a config in enum PLBartConfig
     * @param outputFileName the json file to dump the codex input
     */
    public static void dumpPLBartInput(String filename, int startLine, int endLine, PLBartConfig config, String outputFileName) throws Exception{
        PLBartInput plbartInput = getPLBartInput(filename, startLine, endLine, config);
        plbartInput.dumpAsJson(outputFileName);
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
            PLBartConfig config = null;
            if (args[3].equals("PLBART_SEQFORM_MASKFORM_NOCOMMENT")) {
                config = PLBartConfig.PLBART_SEQFORM_MASKFORM_NOCOMMENT;
            } else if (args[3].equals("PLBART_SEQFORM_COMMENTFORM_NOCOMMENT")) {
                config = PLBartConfig.PLBART_SEQFORM_COMMENTFORM_NOCOMMENT;
            } else {
                throw new Exception("Unrecognized PLBartConfig: " + args[3]);
            }
            String outputFileName = args[4];
            dumpPLBartInput(filename, startLine, endLine, config, outputFileName);
        } else {
            throw new Exception("Arguments number mismatched, expected 5, but got " + args.length);
        }
    }
}
