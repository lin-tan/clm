package clm;

import clm.plbart.PLBartConfig;
import clm.plbart.PLBartInput;
import clm.plbart.PLBartInputParser;

public class TestPLBartInputParser {
    
    /** 
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {
        String usrDir = System.getProperty("user.dir");
        String filename = usrDir + "/src/test/java/clm/Test1.java";
        int startLine = 21;
        int endLine = 22;

        PLBartInput plbartInput = PLBartInputParser.getPLBartInput(filename, startLine, endLine,
                PLBartConfig.PLBART_SEQFORM_MASKFORM_NOCOMMENT);
        System.out.println(plbartInput.toMap());
        System.out.println();

        plbartInput = PLBartInputParser.getPLBartInput(filename, startLine, endLine,
                PLBartConfig.PLBART_SEQFORM_COMMENTFORM_NOCOMMENT);
        System.out.println(plbartInput.toMap());
        System.out.println();

        PLBartInputParser.dumpPLBartInput(filename, startLine, endLine, PLBartConfig.PLBART_SEQFORM_MASKFORM_NOCOMMENT, usrDir + "/src/test/java/clm/plbart_input.json");
    }
}
