package clm.finetuning;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;

import com.fasterxml.jackson.core.JsonGenerationException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class APRData {
    String buggyFunctionBefore;
    String buggyFunctionAfter;
    String buggyLine;
    String fixedLine;

    public APRData(String buggyFunctionBefore, String buggyLine, String buggyFunctionAfter, String fixedLine) {
        this.buggyFunctionBefore = buggyFunctionBefore;
        this.buggyFunctionAfter = buggyFunctionAfter;
        this.buggyLine = buggyLine;
        this.fixedLine = fixedLine;
    }

    public HashMap<String, String> toMap(){
        HashMap<String, String> result = new HashMap<String, String>();
        result.put("buggy function before", this.buggyFunctionBefore);
        result.put("buggy function after", this.buggyFunctionAfter);
        result.put("buggy line", this.buggyLine);
        result.put("fixed line", this.fixedLine);
        return result;
    }

    public void dumpAsJson(String filename) throws JsonGenerationException, JsonMappingException, IOException{
        ObjectMapper writer = new ObjectMapper();
		writer.writeValue(new File(filename), this.toMap());
    }
}
