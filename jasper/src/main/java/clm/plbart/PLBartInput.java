package clm.plbart;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;

import com.fasterxml.jackson.core.JsonGenerationException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class PLBartInput {
    String input;
    String functionRange;

    public PLBartInput(String input, String functionRange) {
        this.input = input;
        this.functionRange = functionRange;
    }

    /** 
     * @return HashMap<String, String>
     */
    public HashMap<String, String> toMap(){
        HashMap<String, String> result = new HashMap<String, String>();
        result.put("input", this.input);
        result.put("function range", this.functionRange);
        return result;
    }

    /** 
     * @param filename
     * @throws JsonGenerationException
     * @throws JsonMappingException
     * @throws IOException
     */
    public void dumpAsJson(String filename) throws JsonGenerationException, JsonMappingException, IOException{
        ObjectMapper writer = new ObjectMapper();
		writer.writeValue(new File(filename), this.toMap());
    }
}
