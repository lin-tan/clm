import sys


DEFECTS4J_OLD_CORRECT = {
    'codet5-small': {
        'CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT': ['Lang_10'],
        'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Chart_20']
    },
    'codet5-base': {
        'CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT': [],
        'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT': []
    },
    'codet5-large': {
        'CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT': ['Mockito_5'],
        'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT': []
    },
    'codegen-350M': {
        'CODEGEN_COMPLETE_CODEFORM_NOCOMMENT': ['Math_98', 'Chart_1', 'Chart_11', 'Closure_46'],
        'CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Chart_1', 'Chart_11', 'Closure_46', 'Math_59']
    },
    'codegen-2B': {
        'CODEGEN_COMPLETE_CODEFORM_NOCOMMENT': [
            'Chart_14', 'Math_98', 'Chart_1', 'Chart_20', 'Closure_57', 'Closure_97', 'Lang_33', 'Lang_40', 'Lang_61', 'Math_96', 'Mockito_34'
        ],
        'CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Chart_1', 'Math_79', 'Chart_8', 'Closure_57', 'Math_85']
    },
    'codegen-6B': {
        'CODEGEN_COMPLETE_CODEFORM_NOCOMMENT': [
            'Math_98', 'Chart_1', 'Chart_11', 'Chart_20', 'Closure_57', 'Closure_125', 'Lang_59', 'Lang_61', 'Math_41', 'Math_70', 'Mockito_34'
        ],
        'CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Closure_46', 'Math_98', 'Chart_1', 'Chart_8', 'Chart_11', 'Chart_24', 'Closure_57', 'Closure_125']
    },
    'plbart-base': {
        'PLBART_SEQFORM_MASKFORM_NOCOMMENT': [
            'Math_98', 'Chart_1', 'Chart_11', 'Chart_20', 'Closure_57', 'Lang_21', 'Lang_43', 'Math_30', 'Math_41', 'Math_57', 'Math_58', 'Mockito_5', 'Mockito_34'
        ],
        'PLBART_SEQFORM_COMMENTFORM_NOCOMMENT': [
            'Closure_46', 'Chart_1', 'Chart_11', 'Lang_21', 'Lang_51', 'Math_57', 'Math_85'
        ]
    },
    'plbart-large': {
        'PLBART_SEQFORM_MASKFORM_NOCOMMENT': [
            'Chart_14', 'Chart_1', 'Chart_11', 'Chart_20', 'Closure_57', 'Lang_21', 'Lang_43', 'Math_41', 'Math_58', 'Math_70', 'Math_85', 'Mockito_5', 'Mockito_34'
        ],
        'PLBART_SEQFORM_COMMENTFORM_NOCOMMENT': [
            'Math_98', 'Chart_1', 'Chart_8', 'Chart_11', 'Lang_21', 'Lang_33', 'Math_27', 'Math_85'
        ]
    },
    'codet5-small-finetune': [
        'Closure_40', 'Math_98', 'Chart_1', 'Chart_11', 'Closure_11', 'Lang_6', 'Lang_21', 'Lang_33', 'Math_30', 'Math_41', 'Math_57', 'Math_59',
        'Math_70', 'Math_80', 'Math_85', 'Math_94', 'Mockito_29', 'Mockito_34', 'Time_19'
    ],
    'codet5-base-finetune': [
        'Chart_14', 'Closure_40', 'Math_98', 'Chart_1', 'Chart_11', 'Chart_12', 'Closure_10', 'Closure_11', 'Closure_57', 'Closure_92', 
        'Closure_97', 'Lang_6', 'Lang_21', 'Lang_26', 'Lang_33', 'Lang_57', 'Math_2', 'Math_30', 'Math_34', 'Math_41', 'Math_57', 
        'Math_59', 'Math_69', 'Math_70', 'Math_80', 'Math_82', 'Math_85', 'Math_94', 'Mockito_34', 'Time_19'
    ],
    'codet5-large-finetune': [
        'Chart_14', 'Closure_40', 'Lang_10', 'Math_98', 'Chart_1', 'Chart_11', 'Chart_24', 'Closure_11', 'Closure_57', 'Closure_86',
        'Closure_92', 'Closure_104', 'Lang_6', 'Lang_21', 'Lang_26', 'Lang_33', 'Lang_57', 'Math_30', 'Math_34', 'Math_41', 'Math_57', 
        'Math_59', 'Math_69', 'Math_70', 'Math_80', 'Math_82', 'Math_85', 'Math_94', 'Mockito_8', 'Mockito_29', 'Mockito_34', 'Mockito_38', 'Time_19'
    ],
    'codegen-350M-finetune': [
        'Closure_40', 'Lang_10', 'Math_98', 'Chart_11', 'Chart_12', 'Chart_24', 'Closure_11', 'Closure_73', 'Lang_6', 'Lang_21', 'Lang_33',
        'Lang_51', 'Math_11', 'Math_57', 'Math_69', 'Math_70', 'Math_80', 'Math_82', 'Math_85', 'Math_94', 'Mockito_29', 'Mockito_34', 'Time_19'
    ],
    'codegen-2B-finetune': [
        'Chart_14', 'Closure_40', 'Math_98', 'Chart_1', 'Chart_8', 'Chart_9', 'Chart_11', 'Chart_12', 'Chart_24', 'Closure_11', 'Closure_57', 
        'Closure_62', 'Closure_73', 'Closure_86', 'Closure_92', 'Closure_104', 'Lang_6', 'Lang_21', 'Lang_26', 'Lang_33', 'Lang_57', 'Math_30', 
        'Math_41', 'Math_57', 'Math_59', 'Math_80', 'Math_82', 'Math_85', 'Math_94', 'Mockito_34', 'Time_4', 'Time_19'
    ],
    'codegen-6B-finetune': [
        'Chart_14', 'Closure_40', 'Lang_10', 'Math_98', 'Chart_1', 'Chart_8', 'Chart_11', 'Chart_12', 'Chart_20', 'Chart_24', 'Closure_11', 'Closure_57', 
        'Closure_62', 'Closure_70', 'Closure_73', 'Closure_86', 'Closure_92', 'Closure_126', 'Lang_21', 'Lang_33', 'Lang_57', 'Lang_59', 'Math_11', 'Math_30', 
        'Math_41', 'Math_57', 'Math_59', 'Math_69', 'Math_70', 'Math_80', 'Math_82', 'Math_85', 'Math_94', 'Mockito_8', 'Mockito_29', 'Mockito_34', 'Time_4', 'Time_19'
    ],
    'plbart-base-finetune': [
        'Closure_40', 'Lang_10', 'Math_98', 'Chart_1', 'Chart_9', 'Chart_11', 'Closure_11', 'Closure_38', 'Closure_73', 'Closure_92', 'Closure_104', 
        'Lang_21', 'Math_30', 'Math_41', 'Math_57', 'Math_59', 'Math_70', 'Math_75', 'Math_80', 'Math_85', 'Math_94', 'Math_96', 'Mockito_29', 
        'Mockito_38', 'Time_19'
    ],
    'plbart-large-finetune': [
        'Closure_40', 'Math_98', 'Chart_1', 'Chart_8', 'Chart_9', 'Chart_11', 'Closure_11', 'Closure_38', 'Closure_73', 'Closure_83', 'Lang_6',
        'Lang_21', 'Lang_33', 'Lang_57', 'Math_2', 'Math_11', 'Math_30', 'Math_34', 'Math_41', 'Math_57', 'Math_59', 'Math_69', 'Math_80', 'Math_85', 
        'Math_94', 'Math_105', 'Mockito_5', 'Mockito_29', 'Time_4', 'Time_19'
    ],
    'CURE': ['Closure_18', 'Closure_70', 'Lang_33', 'Math_75', 'Math_82', 'Time_19'],
    'RewardRepair': [
        'Chart_1', 'Chart_11', 'Closure_18', 'Closure_70', 'Closure_73', 'Closure_92', 'Lang_6', 'Lang_21', 'Lang_33', 'Lang_57', 
        'Lang_59', 'Math_30', 'Math_41', 'Math_70', 'Math_75', 'Math_82', 'Math_94', 'Mockito_26', 'Mockito_38', 'Time_19', 
    ],
    'Recoder': [
        'Closure_14', 'Math_34', 'Lang_6', 'Closure_40', 'Math_58', 'Chart_20', 'Mockito_38', 'Chart_1', 'Math_105', 'Lang_26', 'Closure_70', 
        'Chart_26', 'Math_5', 'Lang_57', 'Math_82', 'Math_27', 'Math_94', 'Closure_10', 'Chart_11', 'Math_75', 'Chart_24', 'Closure_18', 
        'Chart_12', 'Math_85'
    ],
    'Codex': [
        'Chart_14', 'Chart_26', 'Closure_40', 'Closure_123', 'Math_98', 'Chart_1', 'Chart_11', 'Chart_20', 'Closure_5', 'Closure_11', 'Closure_15', 
        'Closure_18', 'Closure_31', 'Closure_35', 'Closure_57', 'Closure_62', 'Closure_73', 'Closure_92', 'Lang_21', 'Lang_33', 'Lang_39', 'Lang_40', 
        'Lang_43', 'Lang_58', 'Lang_59', 'Lang_61', 'Math_5', 'Math_11', 'Math_30', 'Math_41', 'Math_50', 'Math_56', 'Math_57', 'Math_69', 'Math_80', 
        'Math_85', 'Math_91', 'Math_94', 'Math_96', 'Mockito_24', 'Time_4'
    ]
}

DEFECTS4J_NEW_CORRECT = {
    'codet5-small': {
        'CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT': ['JacksonCore_5', 'Jsoup_43'],
        'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Cli_32', 'Jsoup_24', 'Jsoup_40']
    },
    'codet5-base': {
        'CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT': ['Cli_32', 'Compress_31', 'JacksonDatabind_102', 'Jsoup_40'],
        'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Codec_7', 'JacksonDatabind_102']
    },
    'codet5-large': {
        'CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT': ['Jsoup_43'],
        'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Cli_32', 'JacksonDatabind_102']
    },
    'codegen-350M': {
        'CODEGEN_COMPLETE_CODEFORM_NOCOMMENT': ['Cli_8', 'Codec_18', 'Jsoup_57'],
        'CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Jsoup_41', 'Jsoup_57']
    },
    'codegen-2B': {
        'CODEGEN_COMPLETE_CODEFORM_NOCOMMENT': ['Cli_8', 'Codec_7', 'Codec_18', 'Jsoup_57'],
        'CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Cli_8', 'Codec_7', 'Codec_18', 'Jsoup_57']
    },
    'codegen-6B': {
        'CODEGEN_COMPLETE_CODEFORM_NOCOMMENT': ['Codec_7', 'Codec_18', 'JacksonCore_5', 'JacksonCore_25', 'JacksonDatabind_46', 'Jsoup_45', 'Jsoup_51', 'Jsoup_57'],
        'CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT': ['Codec_7', 'Codec_18', 'JacksonCore_5', 'JacksonCore_25']
    },
    'plbart-base': {
        'PLBART_SEQFORM_MASKFORM_NOCOMMENT': [
            'Cli_8', 'Closure_150', 'Compress_19', 'JacksonCore_5', 'JacksonCore_25', 'Jsoup_40', 'Jsoup_43', 'Jsoup_57', 'Jsoup_68'
        ],
        'PLBART_SEQFORM_COMMENTFORM_NOCOMMENT': [
            'Cli_8', 'Codec_7', 'Compress_19', 'Jsoup_40'
        ]
    },
    'plbart-large': {
        'PLBART_SEQFORM_MASKFORM_NOCOMMENT': [
            'Closure_150', 'Codec_7', 'JacksonCore_5', 'JacksonCore_25', 'Jsoup_40', 'Jsoup_45', 'Jsoup_57', 'Jsoup_68'
        ],
        'PLBART_SEQFORM_COMMENTFORM_NOCOMMENT': [
            'Closure_150', 'Codec_7', 'Compress_19', 'JacksonCore_5', 'JacksonCore_25', 'Jsoup_40', 'Jsoup_57', 'Jsoup_68'
        ]
    },
    'codet5-small-finetune': [
        'Cli_28', 'Cli_40', 'Closure_168', 'Codec_7', 'Compress_14', 'Compress_23', 'Csv_4', 'Csv_11', 'JacksonCore_5', 'JacksonCore_8',
        'JacksonCore_25', 'JacksonDatabind_16', 'Jsoup_40', 'Jsoup_68', 'Jsoup_77'
    ],
    'codet5-base-finetune': [
        'Cli_8', 'Cli_28', 'Cli_40', 'Closure_168', 'Codec_7', 'Codec_18', 'Compress_23', 'Csv_4', 'Csv_11', 'JacksonCore_5', 'JacksonCore_8',
        'JacksonCore_25', 'JacksonDatabind_16', 'JacksonDatabind_34', 'Jsoup_40', 'Jsoup_68', 'Jsoup_77'
    ],
    'codet5-large-finetune': [
        'Cli_28', 'Cli_40', 'Closure_168', 'Codec_7', 'Compress_14', 'Compress_19', 'Compress_23', 'Csv_11', 'JacksonCore_5', 'JacksonCore_8',
        'JacksonCore_25', 'JacksonDatabind_16', 'JacksonDatabind_34', 'JacksonDatabind_57', 'JacksonDatabind_71', 'Jsoup_40', 
        'Jsoup_68', 'Jsoup_77', 'Jsoup_86'
    ],
    'codegen-350M-finetune': [
        'Cli_8', 'Cli_28', 'Cli_32', 'Cli_40', 'Closure_168', 'Codec_3', 'Codec_7', 'Collections_26', 'Compress_14', 'Compress_23', 'Compress_27', 
        'Csv_15', 'JacksonCore_5', 'JacksonCore_25', 'JacksonDatabind_76', 'Jsoup_40', 'Jsoup_45', 'Jsoup_57', 'Jsoup_68', 'JxPath_5'
    ],
    'codegen-2B-finetune': [
        'Cli_8', 'Cli_28', 'Cli_40', 'Closure_168', 'Codec_3', 'Codec_7', 'Collections_26', 'Compress_14', 'Compress_19', 'Compress_23', 
        'Csv_15', 'JacksonCore_5', 'JacksonCore_8', 'JacksonCore_25', 'JacksonDatabind_16', 'JacksonDatabind_27', 'JacksonDatabind_34', 
        'JacksonDatabind_76', 'Jsoup_40', 'Jsoup_57', 'Jsoup_68', 'Jsoup_77', 'JxPath_5'
    ],
    'codegen-6B-finetune': [
        'Cli_8', 'Cli_28', 'Cli_32', 'Cli_40', 'Closure_168', 'Codec_3', 'Codec_7', 'Collections_26', 'Compress_14', 'Compress_19', 'Compress_27', 'Csv_11', 
        'Csv_15', 'JacksonCore_5', 'JacksonCore_25', 'JacksonDatabind_16', 'JacksonDatabind_76', 'JacksonDatabind_102', 'Jsoup_24',
        'Jsoup_40', 'Jsoup_43', 'Jsoup_57', 'Jsoup_68'
    ],
    'plbart-base-finetune': [
        'Cli_28', 'Closure_168', 'Codec_7', 'Compress_23', 'Compress_31', 'Csv_11', 'Csv_15', 'JacksonCore_5', 'JacksonCore_25', 'JacksonDatabind_16', 
        'Jsoup_40', 'Jsoup_68', 'Jsoup_77'
    ],
    'plbart-large-finetune': [
        'Cli_28', 'Cli_32', 'Closure_168', 'Codec_7', 'Compress_23', 'Compress_27', 'Compress_31', 'Csv_11', 'Csv_15', 'JacksonCore_5', 'JacksonCore_25', 
        'JacksonDatabind_16', 'JacksonDatabind_34', 'Jsoup_34', 'Jsoup_40', 'Jsoup_45', 'Jsoup_68'
    ],
    'CURE': ['Codec_7', 'Collections_26', 'JacksonCore_5', 'JacksonCore_25', 'JacksonDatabind_16', 'Jsoup_68'],
    'RewardRepair': ['Codec_7', 'Codec_16', 'Collections_26', 'Csv_11', 'JacksonCore_5', 'JacksonCore_25', 'JxPath_10', 'Jsoup_62'],
    'Recoder': [
        'Codec_7', 'Jsoup_61', 'Jsoup_24', 'Closure_168', 'Jsoup_77', 'JacksonCore_5', 'Compress_31', 'JacksonCore_25', 
        'Csv_4', 'Compress_27', 'Compress_19'
    ],
    'Codex': [
        'Cli_4', 'Cli_8', 'Cli_11', 'Cli_25', 'Cli_28', 'Cli_32', 'Codec_2', 'Codec_3', 'Codec_4', 'Compress_23', 'Compress_31', 'Gson_13', 'Gson_15', 
        'Gson_17', 'JacksonCore_5', 'JacksonCore_8', 'JacksonCore_25', 'JacksonDatabind_17', 'JacksonDatabind_27', 'JacksonDatabind_46', 'JacksonDatabind_82', 
        'JacksonDatabind_102', 'Jsoup_40', 'Jsoup_45', 'Jsoup_46', 'Jsoup_57', 'Jsoup_68'
    ]
}

def get_defects4j_correct(model, config=None):
    if config is not None:
        return DEFECTS4J_NEW_CORRECT[model][config] + DEFECTS4J_OLD_CORRECT[model][config]
    return DEFECTS4J_NEW_CORRECT[model] + DEFECTS4J_OLD_CORRECT[model]


def print_correct_num(old=True):
    CORRECT = DEFECTS4J_OLD_CORRECT if old else DEFECTS4J_NEW_CORRECT
    for model in (
        'codet5-small', 'codet5-base', 'codet5-large', 'codegen-350M', 'codegen-2B', 'codegen-6B', 
        'plbart-base', 'plbart-large',
        'codet5-small-finetune', 'codet5-base-finetune', 'codet5-large-finetune', 
        'codegen-350M-finetune', 'codegen-2B-finetune', 'codegen-6B-finetune',
        'plbart-base-finetune', 'plbart-large-finetune',
        'CURE', 'RewardRepair', 'Recoder', 'Codex'
    ):
        if type(CORRECT[model]) == list:
            print(model, len(CORRECT[model]))
        else:
            result = CORRECT[model]
            for prompt in result:
                print(model, prompt, len(result[prompt]))


if __name__ == '__main__':
    old = sys.argv[1] == 'True'
    print(old)
    print_correct_num(old=old)
