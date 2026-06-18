import json
from app.services.llm import client
from app.services.config import AVAILABLE_TOOLS, SYSTEM_PROMPT
import json_repair
from app.services.tools.read import read_file
from app.services.tools.write import write_file
from app.services.tools.bash import run_command
from app.services.tools.edit import edit_file



def parse_response(text):
    if not text:
        raise ValueError("Empty response from AI model")

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        repaired = json_repair.repair_json(text)
        return json.loads(repaired)
    
    except Exception as e:
        pass  
    
    try:
        return json.loads(text)
    
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Failed to parse AI response as JSON:")
        print(f"[ERROR] Raw response (first 500 chars): {text[:500]}")
        raise ValueError(
            f"AI did not return valid JSON. Response starts with: {text[:100]}"
        )
    
    


def execute_tool(response):
    
    tool_name = response.get("tool")
    
    if not tool_name:
        raise ValueError("Missing 'tool' field in response")
    
    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}. Available: {list(AVAILABLE_TOOLS.keys())}")
    
    tool_function = AVAILABLE_TOOLS[tool_name]
    
    if tool_name == "read":
        path = response.get("path")
        if not path:
            raise ValueError("Missing 'path' field for read tool")
        return read_file(path)
    
    elif tool_name == "bash":
        command = response.get("command")
        if not command:
            raise ValueError("Missing 'command' field for bash tool")
        
        result = run_command(command)
        return {
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"]
        }
        
    elif tool_name == "write":
        
        return write_file(
            response["path"],
            response["content"]
        )
        
        
    elif tool_name == "edit":
        
        path = response.get("path", "unknown")
        old_text = response.get("old_text", "unknown")
        new_text = response.get("new_text", "unknown")
        
        return edit_file(path,old_text,new_text)
    
    else:
        return tool_function(response)


def run_agent(prompt): 
    
    
    messages = [
        {
            "role":"system",
            "content": SYSTEM_PROMPT
        },
        {
            "role":"user",
            "content": prompt
        }
    ]
        
    for step in range(100):        

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1
        )
        
        parsed = parse_response(response.choices[0].message.content)
        
        if parsed["tool"] == "final":
            return {
                "success": True,
                "message": parsed["content"]
            }
                            
        tool_name = parsed.get("tool")
        tool_key = None
            
        if tool_name == "read":
            tool_key = f"read:{parsed.get('path')}"

        elif tool_name == "write":
            tool_key = f"write:{parsed.get('path')}"
            files_written_this_turn += 1
            
        elif tool_name == "bash":
            tool_key = f"bash:{parsed.get('command')}"

        elif tool_name == "edit":
            tool_key = f"edit: {parsed.get('path')}"
        
        else:
            tool_key = tool_name
            
        msgs = {
            "read": "→ READING FILE: {path}",
            "bash": "→ RUNNING COMMAND: {command}",
            "write": "→ WRITING: {path}",
            "edit": "→ EDITING: {path}",
        }

        if tool_name in msgs:
            fmt = msgs[tool_name]
            print(fmt.format(**parsed))
            
        else:
            print(f"→ EXECUTING TOOL: {tool_name}")
            print(f"  Parameters: {parsed}")
        
        try:  
            tool_result = execute_tool(parsed)
            
            messages.append(
                {
                    "role":"assistant",
                    "content": json.dumps(parsed)
                }
            )

            messages.append(
                {
                    "role":"user",
                    "content":
                    f"Tool Result:\n{json.dumps(tool_result)}"
                }
            )
        
        except Exception as e:
            tool_result = {
                "error": str(e)
            }
            
            messages.append(
                {
                    "role":"assistant",
                    "content": json.dumps(parsed)
                }
            )

            messages.append(
                {
                    "role":"user",
                    "content": f"Tool Error:\n{json.dumps(tool_result)}"
                }
            )

            continue
        
        
    return "agent exceeded max iteration"
