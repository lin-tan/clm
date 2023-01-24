package clm;

import clm.finetuning.APRData;
import clm.finetuning.FineTuningData;

public class TestFineTuningData {
    public static void main(String[] args) throws Exception {
        String usrDir = System.getProperty("user.dir");
        
        String buggyFilename = usrDir + "/src/test/java/clm/Test1.java";
        int buggyStartLine = 21;
        int buggyEndLine = 21;

        String fixedFilename = usrDir + "/src/test/java/clm/Test1.java";
        int fixedStartLine = 22;
        int fixedEndLine = 22;

        APRData data = FineTuningData.getFineTuningData(buggyFilename, buggyStartLine, buggyEndLine, fixedFilename, fixedStartLine, fixedEndLine);
        System.out.println(data.toMap());
    }
}
