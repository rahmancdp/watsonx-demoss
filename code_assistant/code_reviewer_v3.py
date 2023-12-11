import streamlit as st
import pathlib
import os
import logging
import tempfile
from genai.credentials import Credentials
from genai.schemas import GenerateParams
from genai.exceptions.genai_exception import GenAiException
from genai.model import Model
import os
from dotenv import load_dotenv

def prompt_builder(prompt_template,check_data):
    prompt = f"""{prompt_template}
    {check_data}
    [/INST]
    Output: """
    print("prompt \n\n")
    print(prompt)
    return prompt

  
# define the to be checked code 
unchecked_code_step1 = """import org.springframework.transaction.annotation.Transactional;

    
    public class AnotherTransactionalClass {

        private final ProductRepository productRepository;

        public AnotherTransactionalClass(ProductRepository productRepository) {
            this.productRepository = productRepository;
        }

        public void addProduct(Product product) {
            // Database update operation 1
            productRepository.save(product);
        }

        public void updateProductStock(Product product, int newStock) {
            // Database update operation 2
            product.setStock(newStock);
            productRepository.save(product);
        }

        public void deleteProduct(Product product) {
            // Database update operation 3
            productRepository.delete(product);
        }
    }
    """

unchecked_code_step3= """public Result<TokenVo> login(@RequestBody @Valid LoginForm record) {
        log.info("/hqActivityTemplateAuth/login 请求:{}", record);
        Result result = Result.failure();
        //如果没有活动id或者手机号信息，则返回空
        if (activityMobileCheck(record, result)) {
            return result;
        }
        Map<String, Object> map = authTurntableService.login(record);
        if (Constant.SUCCESSCODE.equals(map.get("code").toString())) {
            result = Result.success();
            TokenVo detail = (TokenVo) map.get("data");
            result.setData(detail);
            return result;
        } else {
            result = Result.failure();
            result.failure(map.get("msg").toString());
            return result;
        """

uncheck_code_example="""package com.faw.sa0214.dcc.service;

import com.faw.sa0214.dcc.dao.DimCycleMappingMapper;
import com.faw.sa0214.dcc.model.po.DimCycleMapping;
import com.faw.sa0214.dcc.model.vo.OperationReportQueryVO;
import org.apache.commons.lang.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.format.DateTimeFormatter;

/**
 * 日期工具服务9
 * @author chenshigui
 * @date 2023-08-15 14:55
 */
@Service
public class DimCycleMappingService {
    public static final String DATE_YYYY_MM_DD = "yyyy-MM-dd";

    public static final DateTimeFormatter DATE_YYYY_MM_DD_FROMATTER = DateTimeFormatter.ofPattern(DATE_YYYY_MM_DD);
    public static final DateTimeFormatter DATE_YYYY_MM_FROMATTER = DateTimeFormatter.ofPattern("yyyy-MM");
    public static final DateTimeFormatter DATE_YYYY_FROMATTER = DateTimeFormatter.ofPattern("yyyy");

    @Autowired
    private DimCycleMappingMapper dimCycleMapper;

    /**
     * 获取时间查询起止时间公共方法
     */
    public void getDateRegion(OperationReportQueryVO queryVo) {
        DimCycleMapping iadDimCycle;
        switch (queryVo.getQueryType()) {
            case "1": // 日
                queryVo.setBeginDate(queryVo.getQueryDate());
                queryVo.setEndDate(queryVo.getQueryDate());
                queryVo.setBeginDayDate(queryVo.getQueryDate());
                queryVo.setEndDayDate(queryVo.getQueryDate());
                break;
            case "6": // 区间
                queryVo.setBeginDayDate(queryVo.getBeginDate());
                queryVo.setEndDayDate(queryVo.getEndDate());
                break;
            case "4": // 季
                iadDimCycle = dimCycleMapper.getDateRegion(queryVo.getQueryType(), queryVo.getQueryDate());
                if(StringUtils.isNotBlank(iadDimCycle.getDateBegin()) && StringUtils.isNotBlank(iadDimCycle.getDateEnd())) {
                    queryVo.setBeginDate(iadDimCycle.getDateBegin().substring(0, 7));
                    queryVo.setEndDate(iadDimCycle.getDateEnd().substring(0, 7));
                    queryVo.setBeginDayDate(iadDimCycle.getDateBegin());
                    queryVo.setEndDayDate(iadDimCycle.getDateEnd());
                }
                break;
            default: // 周月季年
                iadDimCycle = dimCycleMapper.getDateRegion(queryVo.getQueryType(), queryVo.getQueryDate());
                if(StringUtils.isNotBlank(iadDimCycle.getDateBegin()) && StringUtils.isNotBlank(iadDimCycle.getDateEnd())) {
                    queryVo.setBeginDate(iadDimCycle.getDateBegin());
                    queryVo.setEndDate(iadDimCycle.getDateEnd());
                    queryVo.setBeginDayDate(iadDimCycle.getDateBegin());
                    queryVo.setEndDayDate(iadDimCycle.getDateEnd());
                }
                break;
        }
    }


}
"""

instruction1 = """
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.
Apply @Transactional to a Java class, if it contains multiple methods involving database update operations.
If the Java class contains multiple database update and the @Transactioal is missing, add comment begin with // Violation to the and remind that @Transnational is required.
If there is no violation, don't add any comment of the code. Just say No violation
"""
instruction2 = """
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.
The rules are: 
If values are passed into a method as input,  log the input value in the first line of the function, it can be logged by any logging framwork like log4j or SLF4J, and usually start with prefix log, like log.info, log.debug.
If the logging is missed, Add comment to begin with // Violation and remind to log the passed value.
If the logging like "log.info", "log.debug" exist, just say No Violation. 
If there is an exceptions caught and not the exception is not logged .Add comment to begin with // Violation and remind to log the exception
Do not modify or correct the original code, finish the review by adding <end-fo-code> in the end. 
"""

rule1 = """
Input: @Transactional(rollbackFor = Exception.class)
public class SampleServiceImpl extends BaseServiceImpl<SampleMapper, SampleEntity> implements SampleService {

    public void updateOperation1() {
        // Database update operation 1
    }

    public void updateOperation2() {
        // Database update operation 2
    }

    public void performTransaction() {
        // Call multiple update operations within a transaction.
        updateOperation1();
        updateOperation2();
    }
}

Output: No Violation 
"""

rule2 = """
Input: public class Example1 {

    public class SampleService {

        public void updateOperation1() {
            // Database update operation 1
            // This method is not part of any transaction
        }

        public void updateOperation2() {
            // Database update operation 2
            // This method is not part of any transaction
        }

        public void performOperationsWithoutTransaction() {
            // Call multiple update operations without a transaction.
            updateOperation1();
            updateOperation2();
        }
    }
}

Output: // Violation, Missing Transnational annotation  
public class Example1 {

    public class SampleService {

        public void updateOperation1() {
            // Database update operation 1
            // This method is not part of any transaction
        }

        public void updateOperation2() {
            // Database update operation 2
            // This method is not part of any transaction
        }

        public void performOperationsWithoutTransaction() {
            // Call multiple update operations without a transaction.
            updateOperation1();
            updateOperation2();
        }
    }
}
<end-of-code>
"""

rule3 = """
Input: import org.springframework.transaction.annotation.Transactional;

@Transactional
public class TransactionalClass {

    private final UserRepository userRepository;

    public TransactionalClass(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public void updateUserProfile(User user, String newProfile) {
        // Database update operation 1
        user.setProfile(newProfile);
        userRepository.save(user);
    }

    public void increaseUserPoints(User user, int pointsToAdd) {
        // Database update operation 2
        user.setPoints(user.getPoints() + pointsToAdd);
        userRepository.save(user);
    }
}



Output:  No Violation

<end-of-code>
"""
rule4 = """
Input: public class ViolatingTransactionalClass {

    private final UserRepository userRepository;

    public ViolatingTransactionalClass(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public void updateUserProfile(User user, String newProfile) {
        // Database update operation 1
        user.setProfile(newProfile);
        userRepository.save(user);
    }

    public void increaseUserPoints(User user, int pointsToAdd) {
        // Database update operation 2
        user.setPoints(user.getPoints() + pointsToAdd);
        userRepository.save(user);
    }
}

Output: // Violation,  Transnational annotation is required   
public class ViolatingTransactionalClass {

    private final UserRepository userRepository;

    public ViolatingTransactionalClass(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public void updateUserProfile(User user, String newProfile) {
        // Database update operation 1
        user.setProfile(newProfile);
        userRepository.save(user);
    }

    public void increaseUserPoints(User user, int pointsToAdd) {
        // Database update operation 2
        user.setPoints(user.getPoints() + pointsToAdd);
        userRepository.save(user);
    }
}
<end-of-code>
"""

rule5 = """
Input: public class AnotherViolatingTransactionalClass {

    private final ProductRepository productRepository;

    public AnotherViolatingTransactionalClass(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }


    public void addProduct(Product product) {
        // Database update operation 1
        productRepository.save(product);
    }

    public void updateProductStock(Product product, int newStock) {
        // Database update operation 2
        product.setStock(newStock);
        productRepository.save(product);
    }
}

Output: // Violation,  Transnational annotation  is required 
import org.springframework.transaction.annotation.Transactional;

public class AnotherViolatingTransactionalClass {

    private final ProductRepository productRepository;

    public AnotherViolatingTransactionalClass(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }


    public void addProduct(Product product) {
        // Database update operation 1
        productRepository.save(product);
    }

    public void updateProductStock(Product product, int newStock) {
        // Database update operation 2
        product.setStock(newStock);
        productRepository.save(product);
    }
}
<end-of-code>
"""

rule6 = """
Input: public class NoTransactionalClass2 {

    private final ProductRepository productRepository;

    public NoTransactionalClass2(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public void addProduct(Product product) {
        // Database update operation 1
        productRepository.save(product);
    }

    public void updateProductStock(Product product, int newStock) {
        // Database update operation 2
        product.setStock(newStock);
        productRepository.save(product);
    }
}

Output: // Violation,  Transnational annotation  is required 
public class NoTransactionalClass2 {

    private final ProductRepository productRepository;

    public NoTransactionalClass2(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public void addProduct(Product product) {
        // Database update operation 1
        productRepository.save(product);
    }

    public void updateProductStock(Product product, int newStock) {
        // Database update operation 2
        product.setStock(newStock);
        productRepository.save(product);
    }
}
<end-of-code>
"""
rule7 = """
Input: catch (Exception e) 
{
return false;
}
Output: catch (Exception e) 
{
  // Violation:  Logging needed
return false;
}
<end-of-code>
"""
rule8 = """
Input: public Result<UserInfo> login(@RequestBody @Valid LoginForm Productname) {
     log.info("/my/test/{}}", Productname);
     Result<UserInfo> result = Result.failure();
    return result;
}

Output: No Violation

<end-of-code>
"""

rule9 = """
Input: public Result<UserInfo> login(@RequestBody @Valid LoginForm Productname) {
     
     Result<UserInfo> result = Result.failure();
    return result;
}

Output: public Result<UserInfo> login(@RequestBody @Valid LoginForm Productname) {
      // Violation:  Logging needed
     Result<UserInfo> result = Result.failure();
    return result;
}

<end-of-code>
"""

rule10 = """
Input: catch (Exception e) 
{
log.info("/my/test/error:{}}", e);
return false;
}
Output: No Violation

<end-of-code>
"""

cotstep1 = """[INST] <<SYS>>
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.
Do the following jobs step by step.
1. Understand the code structure and find out the java methods and body
2. Check if "baseMapper.update","baseMapper.delete" ,"baseMapper.save"  property are used in all found java methods body. "baseMapper.select" not count here, if "baseMapper.select" is found skip to the following steps.
3. If  property "baseMapper.update","baseMapper.delete" ,"baseMapper.save"  found in any methods, then check if @Transactional annotation was included in that method, ignore "baseMapper.select".  if "baseMapper.select" is found skip to the following steps.
4  If  property "baseMapper.update","baseMapper.delete" ,"baseMapper.save"  found in any methods and If @Transactional annotation is missing it violate the rule as @Transnational is required.  Ignore "baseMapper.select".  if "baseMapper.select" is found skip to the following steps.
5  Last, Give a final summary about your conclusion of violation with word "Summary".   
Do not change or correct any of the input code.In the end of review, add <end-of-code>. 
<</SYS>>
java:`{code}`
[/INST]
review:"""

cotstep2 = """[INST] <<SYS>>
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.
Do the work step by step.
 1. Understand the code structure , find the java methods annotation and its input if exist.
2. If the found annotation in step 1 does not includes Spring Web module like @PostMapping @GetMapping and similar , skip to last steps directly.
3. If the found annotation in step 1 includes Spring Web module like @PostMapping @GetMapping and similar , check if the methods have input variable.  If the found annotation in step 1 does not includes Spring Web module like @PostMapping @GetMapping and similar , skip to last steps directly.
4. In the condition of the Spring Web module like @PostMapping @GetMapping or similar in the annotation, and the methods have input variable, check the method body,  it is required to have logging of the passed in values.  
5.  If the Spring Web module like @PostMapping @GetMapping or similar in the annotation exist, and the methods have input variable, and If the logging is missed, it violate the rule.
6. Give final summary based on above steps with words  Summary.  
Do not modify or correct the original code, finish the review by adding <end-fo-code> in the end. 
<</SYS>>
java:`{code}`
[/INST]
review:"""

cotstep3 = """[INST] <<SYS>>
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect. Do the following work step by step.
1. Understand the code structure and find out the java methods declarations and the return value parts.
2. In the method declaration return values, direct use of reserved words "Object" is violate, For example Info(Object) is violate.
3. All other return types are not violate,  for example Page<EvSupplementaryInformationDTO> is not violate because it does not include  reserved words "Object".
4. Give final summary based on above steps with words  Summary.  
Do not change or correct any of the input code.In the end of review, add <end-of-code>. 
<</SYS>>
java:`{code}`
[/INST]
review:"""

cotstep4 = """[INST] <<SYS>>
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.Do the work step by step.
1. Understand the code structure , find all java method definition and method call, and the their name.
2. Use your knowledge to guess from the method name that if this method is working on database aggregation operation.
3. If you think this method or method call is about  database aggregation operation, check the return value type. It is violate if it use Map or Hashmap as return type.
4. If you think this method or method call is about  database aggregation operation, finish the code review. 
5. Give final summary based on above steps with words begin with Summary.  
Do not modify or correct the original code, finish the review by adding <end-fo-code> in the end. 
<</SYS>>
java:`{code}`
[/INST]
review:"""

cotstep5 = """[INST] <<SYS>>
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.
Do the work step by step.
1. Understand the code structure , find all java method and its methods annotation.
2. If the methods annotation does not includes Spring Web module like @PostMapping @GetMapping and similar ,  skip all following steps and finish the review. 
3. If the methods annotation includes Spring Web module like @PostMapping @GetMapping and similar,  check if the @ApiOperation or @API annotation is also exist for that method.
4. If Spring Web module like @PostMapping @GetMapping and similar, but can't find @ApiOperation Mapping, it is violation as it needed for documentation propose . 
5. Give final summary based on above steps with words begin with Summary.  
Do not modify or correct the original code, finish the review by adding <end-fo-code> in the end. 
<</SYS>>
java:`{code}`
[/INST]
review:"""

cotstep6 = """[INST] <<SYS>>
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.
Do the work step by step.
1. Understand the code structure , find all java method and its methods annotation.
2. Find if there is any parts of the code using numeric values directly in method body or method call.  If it is found, it is violate. 
3. Give a final summary with word Summary, it needs include the code which violate the rule and reason of violation. Don't need to have fix suggestion. 
Do not modify or correct the original code, finish the review by adding <end-fo-code> in the end. 
<</SYS>>
java:`{code}`
[/INST]
review:"""

cotstep7 = """[INST] <<SYS>>
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.
Do the work step by step, and tell me your analysis
1. Understand the code structure , find the java method declarations line in the code.
2. If there is no method declarations in the code, skip the following steps, and finish the review/
3. If methods declarations found, use your knowledge to guess if the method name is meaningful with semantic expression; If not, it is violate. 
4. Give a final summary,  with words Summary, and include the method name which violate if there is one. 
Do not modify or correct the original code, finish the review by adding <end-fo-code> in the end. 
<</SYS>>
java:`{code}`
[/INST]
review:"""

cotstep8 = """[INST] <<SYS>>
You are a experienced Java programmer, your job is to review others Java code, and focus on the rules below only, you don't need to review other aspect.
The rule is:
Java method , Java enum should have comment in place, 
Do the work step by step.
1. Understand the code structure , find all java method and its methods comment.
2. Use your knowledge to understand the methods, if it is easy a programmer to understand, then no need to add comment; 
3. If the method is complex and no comment provided within the method, then it violate the rule.
4. Give a final summary in English  with words Summary, don't need to included suggested comment.
Finish the review by adding <end-of-code> in the end. 
<</SYS>>
java:`{code}`
[/INST]
review:"""

step0 = """[INST]as code reviewer, help review the following java code, locate the problem and give advise.
<<SYS>>
java:`{code}`
<<SYS>>
[/INST]
review:"""

def splitcode(unchecked_code):
    totallen = len(unchecked_code)
    print(totallen)
    codes = []
    start = 0
    step = 2000
    while start <= totallen:
        codes += [unchecked_code[start:start+step]]
        start += step
    print(len(codes))
    return codes

def reviewer(filename,unchecked_code):
    
    steps = [cotstep1,cotstep2, cotstep3,cotstep4,cotstep5,cotstep6,cotstep7,cotstep8]
    steps_list = ["Rule#1 Transcation Check", "Rule#2 Log Check", "Rule#3 Object Return Check", "Rule#4 Map Return Check", "Rule#5 Swagger Annoation Check", "Rule#6 Magic Value Check", "Rule#7 Naming Convension Check","Rule#8 Comment Check"]

    for promptitr, desc in zip(steps,steps_list):
        st.markdown('#### '+desc)
        totallen = len(unchecked_code)
        codes = splitcode(unchecked_code)
        prompts = []
        for code in codes:
            prompts += [promptitr.format(code=code)]

        checked_code = ""
        
        with st.spinner('Reviewing'):
            for response in llmllama.generate_async(prompts):
                if response is not None:
                    checked_code += response.generated_text

        summary = ""
        with st.spinner('Reviewing'):
            try:
                for response in llmsummary.generate([f"""[INST]summary the following comment.
                                        comments: {checked_code[0:3000]}
                                        [/INST]
                                        summary:"""]):
                    summary += response.generated_text
            except GenAiException as e:
                print("too many token"+len(checked_code))
        
        st.markdown(summary)
    
    
if __name__ == "__main__":
    load_dotenv()
    api_key = st.secrets["GENAI_KEY"]
    api_endpoint = st.secrets["GENAI_API"]

    api_key = os.getenv("GENAI_KEY", None)
    api_endpoint = os.getenv("GENAI_API", None)

    creds = Credentials(api_key,api_endpoint)

    params = GenerateParams(
        decoding_method="greedy",
        max_new_tokens=4000,
        min_new_tokens=10,
        top_k=50,
        top_p=1,
        stop_sequences=["<end-of-code>"],
        # repetition_penalty=1,
    )

    # llmstarcoder = Model(model="bigcode/starcoder",credentials=creds, params=params)
    llmllama = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)
    llmsummary = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

    temp_dir = tempfile.TemporaryDirectory()

    st.set_page_config(layout="wide")
    st.header("code quality assistant powered by watsonx")

    incode = ""
    outcode = ""
    outdocumenation = ""
    uploaded_files = []

    colsource, colreview = st.columns(2)

    with colsource:
        uploaded_files = st.file_uploader(label="upload a java source code file",type=['java'],accept_multiple_files=True)
        for file in uploaded_files:
            st.write("filename:", file.name)
            with open(os.path.join(pathlib.Path(temp_dir.name),file.name),"wb") as f:
                f.write(file.getbuffer())
                incode = file.read().decode()
                st.code(incode,language="java")

    with colreview:
        reviewbutton = st.button("review")
        if reviewbutton:
            for file in uploaded_files:
                st.text('Reviewing Code is running...')
                reviewer(file.name,incode)