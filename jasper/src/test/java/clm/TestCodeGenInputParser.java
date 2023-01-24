package clm;

import clm.codegen.CodeGenConfig;
import clm.codegen.CodeGenInput;
import clm.codegen.CodeGenInputParser;

public class TestCodeGenInputParser {
    
    
    /** 
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {
        String usrDir = System.getProperty("user.dir");
        String filename = usrDir + "/src/test/java/clm/Test1.java";
        int startLine = 21;
        int endLine = 22;

        CodeGenInput codegenInput = CodeGenInputParser.getCodeGenInput(filename, startLine, endLine, CodeGenConfig.CODEGEN_COMPLETE_CODEFORM_NOCOMMENT);
        System.out.println(codegenInput.toMap());
        System.out.println();

        codegenInput = CodeGenInputParser.getCodeGenInput(filename, startLine, endLine, CodeGenConfig.CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT);
        System.out.println(codegenInput.toMap());
        System.out.println();

        CodeGenInputParser.dumpCodeGenInput(filename, startLine, endLine, CodeGenConfig.CODEGEN_COMPLETE_CODEFORM_NOCOMMENT, usrDir + "/src/test/java/clm/codegen_input.json");
    }
}
