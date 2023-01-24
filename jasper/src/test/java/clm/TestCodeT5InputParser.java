package clm;

import clm.codet5.CodeT5Config;
import clm.codet5.CodeT5Input;
import clm.codet5.CodeT5InputParser;

public class TestCodeT5InputParser {
    
    /** 
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {
        String usrDir = System.getProperty("user.dir");
        String filename = usrDir + "/src/test/java/clm/Test1.java";
        int startLine = 21;
        int endLine = 22;

        CodeT5Input codet5Input = CodeT5InputParser.getCodeT5Input(filename, startLine, endLine,
                CodeT5Config.CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT);
        System.out.println(codet5Input.toMap());
        System.out.println();

        codet5Input = CodeT5InputParser.getCodeT5Input(filename, startLine, endLine,
                CodeT5Config.CODET5_REFINE_CODEFORM_NOCOMMENT);
        System.out.println(codet5Input.toMap());
        System.out.println();

        codet5Input = CodeT5InputParser.getCodeT5Input(filename, startLine, endLine,
                CodeT5Config.CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT);
        System.out.println(codet5Input.toMap());
        System.out.println();

        CodeT5InputParser.dumpCodeT5Input(filename, startLine, endLine, CodeT5Config.CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT, usrDir + "/src/test/java/clm/codet5_input.json");
    }
}
