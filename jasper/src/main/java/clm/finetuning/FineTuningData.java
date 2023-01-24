package clm.finetuning;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;

import com.github.javaparser.ast.Node;

import clm.jasper.ContextParser;
import clm.jasper.Parser;

public class FineTuningData {
    public static void wrapFunction(String code, String filepath) throws Exception {
		Node root = Parser.parseMethodDeclaration(code, true);
		BufferedWriter bw = new BufferedWriter(new FileWriter(new File(filepath)));
		String str = "public class DummyClass {\n" + root.toString() + "\n}";
		bw.write(str);
		bw.close();
	}

    public static APRData getFineTuningData(String buggyFilename, int buggyStartLine, int buggyEndLine, 
        String fixedFilename, int fixedStartLine, int fixedEndLine) {
        try {
            String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(buggyFilename, buggyStartLine, buggyEndLine, true);
            String buggyLine = ContextParser.getDedentedCode(buggyFilename, buggyStartLine, buggyEndLine, true);
            String buggyFunctionAfter = ContextParser.getSurroundingFunctionAfter(buggyFilename, buggyStartLine, buggyEndLine, true);

            String fixedLine = ContextParser.getDedentedCode(fixedFilename, fixedStartLine, fixedEndLine, true);
            
            buggyFunctionBefore = Parser.removeEmptyLines(buggyFunctionBefore);
            buggyFunctionAfter = Parser.removeEmptyLines(buggyFunctionAfter);
            buggyLine = Parser.removeEmptyLines(buggyLine);
            fixedLine = Parser.removeEmptyLines(fixedLine);

            return new APRData(buggyFunctionBefore + "\n", buggyLine + "\n", buggyFunctionAfter + "\n", fixedLine + "\n");
        } catch (Exception e){
            return new APRData("", "", "", "");
        }
    }

    public static void dumpFineTuningData(String buggyFilename, int buggyStartLine, int buggyEndLine, 
        String fixedFilename, int fixedStartLine, int fixedEndLine, String outputFilename) throws Exception {
        APRData data = FineTuningData.getFineTuningData(buggyFilename, buggyStartLine, buggyEndLine, fixedFilename, fixedStartLine, fixedEndLine);
        data.dumpAsJson(outputFilename);
    }

    public static APRData getInferenceFineTuningInput(String buggyFilename, int buggyStartLine, int buggyEndLine) {
        try {
            String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(buggyFilename, buggyStartLine, buggyEndLine, true);
            String buggyLine = ContextParser.getDedentedCode(buggyFilename, buggyStartLine, buggyEndLine, true);
            String buggyFunctionAfter = ContextParser.getSurroundingFunctionAfter(buggyFilename, buggyStartLine, buggyEndLine, true);

            buggyFunctionBefore = Parser.removeEmptyLines(buggyFunctionBefore);
            buggyFunctionAfter = Parser.removeEmptyLines(buggyFunctionAfter);
            buggyLine = Parser.removeEmptyLines(buggyLine);

            return new APRData(buggyFunctionBefore + "\n", buggyLine + "\n", buggyFunctionAfter + "\n", "");
        } catch (Exception e){
            return new APRData("", "", "", "");
        }
    }

    public static void dumpInferenceFineTuningData(String buggyFilename, int buggyStartLine, int buggyEndLine, String outputFilename) throws Exception {
        APRData data = getInferenceFineTuningInput(buggyFilename, buggyStartLine, buggyEndLine);
        data.dumpAsJson(outputFilename);
    }

    public static void main(String[] args) throws Exception {
        if (args.length == 8 && args[0].equals("finetuning")) {
            String buggyFilename = args[1];
            int buggyStartLine = Integer.parseInt(args[2]);
            int buggyEndLine = Integer.parseInt(args[3]);
            String fixedFilename = args[4];
            int fixedStartLine = Integer.parseInt(args[5]);
            int fixedEndLine = Integer.parseInt(args[6]);
            String outputFilename = args[7];
            dumpFineTuningData(buggyFilename, buggyStartLine, buggyEndLine, fixedFilename, fixedStartLine, fixedEndLine, outputFilename);
        } else if (args.length == 5 && args[0].equals("finetuning")) {
            String code1 = args[1], code2 = args[3];
			String filepath1 = args[2], filepath2 = args[4];
			wrapFunction(code1, filepath1);
			wrapFunction(code2, filepath2);
        } else if (args.length == 5 && args[0].equals("inference")) {
            String buggyFilename = args[1];
            int buggyStartLine = Integer.parseInt(args[2]);
            int buggyEndLine = Integer.parseInt(args[3]);
            String outputFilename = args[4];
            dumpInferenceFineTuningData(buggyFilename, buggyStartLine, buggyEndLine, outputFilename);
        } else {
            throw new Exception("Arguments number mismatched, expected 8/5, but got " + args.length);
        }
    }
}
