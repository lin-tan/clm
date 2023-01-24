package clm;

import com.github.javaparser.ast.Node;

import clm.jasper.ContextParser;
import clm.jasper.Parser;

public class TestParser {
    
    /** 
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {
        String usrDir = System.getProperty("user.dir");
        String filename = usrDir + "/src/test/java/clm/Test1.java";
        int startLine = 21;
        int endLine = 21;

        Node root = Parser.parseFile(filename, true);
        System.out.println("file: \n" + root);
        System.out.println();

        String buggyCode = Parser.getCode(filename, startLine, endLine);
        System.out.println("buggy code: \n" + buggyCode);
        System.out.println();

        String buggyFunction = ContextParser.getSurroundingFunction(root, buggyCode, startLine, endLine);
        System.out.println("buggy function: \n" + buggyFunction);
        System.out.println();

        String buggyFunctionBefore = ContextParser.getSurroundingFunctionBefore(filename, startLine, endLine, true);
        System.out.println("buggy function before: \n" + Parser.removeEmptyLines(buggyFunctionBefore));
        System.out.println();

        String buggyFunctionAfter = ContextParser.getSurroundingFunctionAfter(filename, startLine, endLine, true);
        System.out.println("buggy function after: \n" + Parser.removeEmptyLines(buggyFunctionAfter));
        System.out.println();
    }
}
