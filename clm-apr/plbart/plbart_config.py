PLBartInputConfig = {
    "PLBART_SEQFORM_MASKFORM_NOCOMMENT": {
        "model_id": "plbart-base/large",
        "input": "entire buggy function, with buggy lines masked by <mask>",
        "patch": "code generated by the model, which will replace the buggy function"
    },
    "PLBART_SEQFORM_COMMENTFORM_NOCOMMENT": {
        "model_id": "plbart-base/large",
        "input": "entire buggy function, with comments telling the buggy lines and buggy lines masked by <mask>",
        "patch": "code generated by the model, which will replace the buggy function"
    }
}