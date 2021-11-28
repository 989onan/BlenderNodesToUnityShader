bl_info = {
    "name": "Blender Material To Unity Shader",
    "author": "989onan, contributors on GitHub",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Shader Blender To Unity (Create Tab)",
    "description": "Converts the selected object's materials into"
                   "Unity3D Shader files (VERY ALPHA)",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

import bpy
import random
import string
import copy
import numpy




def readNodeTrees(all):
    output = []
    
    if(all == True):
        materialslots = bpy.context.active_object.material_slots
    else:
        materialslots = [bpy.context.active_object.active_material]
    
    bpy.context.scene.BlToUnShader_debugfile = ""
    bpy.context.scene.BlToUnShader_uvtex = ""
    unsupported = ["BEVEL","AMBIENT_OCCLUSION","ATTRIBUTE","BACKGROUND","BLACKBODY","BSDF_ANISOTROPIC","BSDF_HAIR","BSDF_HAIR_PRINCIPLED","BSDF_VELVET","DISPLACEMENT","EEVEE_SPECULAR","NEW_GEOMETRY","OUTPUT_AOV","OUTPUT_LIGHT","OUTPUT_LINESTYLE","OUTPUT_WORLD","PARTICLE_INFO","SUBSURFACE_SCATTERING","TEX_WHITE_NOISE","UVALONGSTROKE","VECTOR_DISPLACEMENT","VOLUME_ABSORPTION","VOLUME_INFO","PRINCIPLED_VOLUME","VOLUME_SCATTER","BSDF_REFRACTION","BSDF_TOON","BSDF_TRANSLUCENT","GROUP","HOLDOUT","LIGHT_FALLOFF","LIGHT_PATH","NORMAL","NORMAL_MAP","TEX_IES","WAVELENGTH"]
    materialDataArray = []
    writedebug("START OF CONVERSION TRANSCRIPT!")
    
    
    for materialslot in materialslots:
        if(all):
            material = materialslot.material
        else:
            material = materialslots[0]
        nodetree = material.node_tree
        nodes = nodetree.nodes
        
        
        
        letters = string.ascii_lowercase
        locals = ""
        globals = ""
        inputs = ""
        
        nodenames = []
        
        imagenames = set()
        enviromentnames = set()
        
        noiseNeeded = False 
        
        for node in nodes:
            
            node.label = ( ''.join(random.choice(letters) for i in range(10)) )
            while node.label in nodenames or node.label == "placeholder":
                node.label = ( ''.join(random.choice(letters) for i in range(10)) )
            nodenames.append(node.label)
            #check if the node is supported before anything else.
            if(node.type in unsupported):
                #writedebug(node.type + " with the name "+node.label+" is unsupported and possibly Blender 3D only!  I would give you a gold star to implement this one!")
                continue
            
            run = "define_"+node.type+"(node.label"
            if(node.type == "TEX_IMAGE" or node.type == "TEX_ENVIROMENT"):
                if(node.image):
                    imagenames.add(node.image.name)
            if(node.type == "VALUE"):
                run += ","+str(node.outputs[0].default_value)
            
            
            run += ")"
            
            
            #grab the data that is needed to initalize this type of node
            varibles = ["","",""]
            varibles = eval(run)
            
                        
            #let the node types define themselves
            if(not varibles[0] == ""):
                locals += "\n            "+varibles[0]
            if(not varibles[1] == ""):
                globals += "\n            "+varibles[1]
            if(not varibles[2] == ""):
                inputs += "\n        "+varibles[2]
                
            if(node.type == "TEX_BRICK" or node.type == "TEX_NOISE"):
                noiseNeeded = True
            
            
        if(noiseNeeded):
            inputs += "\n        _noise_input(\"put the Blender3D noise texture in here!!!\", 2D) = \"white\" {}"
            globals += "\n            sampler2D _noise_input;"
        
        
        #this gets an item from image names and puts it in bpy.types.Scene.BlToUnShader_uvtex 
        
        if(len(imagenames) == 0):
            bpy.context.scene.BlToUnShader_uvtex = "placeholder_Texture"
        else:
            for name in imagenames:
                bpy.context.scene.BlToUnShader_uvtex = name+"_Texture"
                break
            
        for imagename in enviromentnames:
            inputs += "\n    _"+imagename+"_Cube(\"Enviroment Texture \'"+imagename+"\'\", Cube) = \"\" {}"
            globals += "\n            "+"samplerCUBE _"+imagename+"_Cube;"
        
        if(len(imagenames) == 0):
            imagename = "placeholder"
            inputs += "\n    [HideInInspector]_"+imagename+"_Texture(\"Image Texture \'"+imagename+"\'\", 2D) = \"white\" {}"
            globals += "\n            "+"sampler2D _"+imagename+"_Texture;"
        else:
            for imagename in imagenames:
                inputs += "\n    _"+imagename+"_Texture(\"Image Texture \'"+imagename+"\'\", 2D) = \"white\" {}"
                globals += "\n            "+"sampler2D _"+imagename+"_Texture;"
        
        writedebug("\nimage names: "+str(imagenames))
        writedebug("\nenviroment names: "+str(enviromentnames))
        materialDataArray.append([material,locals,globals,inputs])
    return materialDataArray


def writedebug(string):
    if(bpy.context.scene.BlToUnShader_debugmode == True):
        print(string)
        bpy.context.scene.BlToUnShader_debugfile += string
        



def writeNodeData(material,locals,globals,inputs):
    
    unsupported = ["ShaderNodeBevel","ShaderNodeAmbientOcclusion","ShaderNodeAttribute","ShaderNodeBackground","ShaderNodeBlackbody","ShaderNodeBsdfAnisotropic","BSDF_HAIR","BSDF_HAIR_PRINCIPLED","BSDF_VELVET","DISPLACEMENT","EEVEE_SPECULAR","NEW_GEOMETRY","OUTPUT_AOV","OUTPUT_LIGHT","OUTPUT_LINESTYLE","OUTPUT_WORLD","PARTICLE_INFO","SUBSURFACE_SCATTERING","TEX_WHITE_NOISE","UVALONGSTROKE","VECTOR_DISPLACEMENT","VOLUME_ABSORPTION","VOLUME_INFO","PRINCIPLED_VOLUME","VOLUME_SCATTER","BSDF_REFRACTION","BSDF_TOON","BSDF_TRANSLUCENT","GROUP","HOLDOUT","LIGHT_FALLOFF","LIGHT_PATH","NORMAL","NORMAL_MAP","TEX_IES","WAVELENGTH"]
    
    #start our code string
    NewCode = ""
    
    
    #make helper functions and start our code
    NewCode += "//Generated using 989onan's Blender To Unity Addon!"
    NewCode += "\nShader \"Blender3D/"+material.name+"\""
    NewCode += "\n{"
    NewCode += "\n    Properties"
    NewCode += "\n    {"
    NewCode += inputs #put in our input textures and parameters
    NewCode += "\n    }"
    NewCode += "\n    SubShader"
    NewCode += "\n    {"
    NewCode += "\n        Tags { \"RenderType\"=\"Opaque\" }"
    NewCode += "\n        LOD 200"
    NewCode += "\n        "
    NewCode += "\n        CGPROGRAM"
    NewCode += "\n        // Physically based Standard lighting model, and enable shadows on all light types"
    NewCode += "\n        #pragma surface surf Standard fullforwardshadows vertex:vert"
    NewCode += "\n        "
    NewCode += "\n        // Use shader model 4.0 target, to fix annoying bugs"
    NewCode += "\n        #pragma target 4.0"
    NewCode += "\n        "
    NewCode += "\n        struct Input"
    NewCode += "\n        {"
    NewCode += "\n            float2 uv_"+bpy.context.scene.BlToUnShader_uvtex+";"
    NewCode += "\n            INTERNAL_DATA"
    NewCode += "\n            float3 viewDir;"
    NewCode += "\n            float3 worldNormal;"
    NewCode += "\n            float4 screenPos;"
    NewCode += "\n            float3 worldRefl;"
    NewCode += "\n            float2 InputUV : TEXCOORD0;"
    NewCode += "\n            float4 vertexColor;"
    NewCode += "\n            float4 worldPos;"
    NewCode += "\n        };"
    NewCode += "\n        void vert (inout appdata_full v, out Input o) //CREDIT: http://answers.unity.com/answers/928498/view.html"
    NewCode += "\n        {"
    NewCode += "\n            UNITY_INITIALIZE_OUTPUT(Input,o);"
    NewCode += "\n            o.vertexColor = v.color; // Save the Vertex Color in the Input for the surf() method"
    NewCode += "\n            float3 worldPos = mul (unity_ObjectToWorld, v.vertex).xyz;"
    NewCode += "\n            o.worldPos = float4(worldPos,0.0);"
    NewCode += "\n        }"
    NewCode += "\n        float3 hsv2rgb( in float3 c )"
    NewCode += "\n        {"
    NewCode += "\n            float3 rgb = clamp( abs(((c.x*6.0+float3(0.0,4.0,2.0))%6.0)-3.0)-1.0, 0.0, 1.0 );"
    NewCode += "\n            return c.z * lerp( float3(1.0,1.0,1.0), rgb, c.y);"
    NewCode += "\n        }"
    NewCode += "\n        /*void axis_angle_to_mat3(in float mat[3][3], float4 axis4, float angle)"
    NewCode += "\n        {"
    NewCode += "\n           float nor[3], nsi[3], co, si, ico;"
    NewCode += "\n           "
    NewCode += "\n           "
    NewCode += "\n           axis = float4(axis4.x,axis4.y,axis4.z); //injected code from @989onan"
    NewCode += "\n           "
    NewCode += "\n           // normalise the axis first (to remove unwanted scaling) (changed by @989onan)"
    NewCode += "\n           axis = normalize(axis);"
    NewCode += "\n           "
    NewCode += "\n           // now convert this to a 3x3 matrix "
    NewCode += "\n           co= (float)cos(angle);"   
    NewCode += "\n           si= (float)sin(angle);"
    NewCode += "\n           "
    NewCode += "\n           ico= (1.0f - co);"
    NewCode += "\n           nsi[0]= nor[0]*si;"
    NewCode += "\n           nsi[1]= nor[1]*si;"
    NewCode += "\n           nsi[2]= nor[2]*si;"
    NewCode += "\n           "
    NewCode += "\n           mat[0][0] = ((nor[0] * nor[0]) * ico) + co;"
    NewCode += "\n           mat[0][1] = ((nor[0] * nor[1]) * ico) + nsi[2];"
    NewCode += "\n           mat[0][2] = ((nor[0] * nor[2]) * ico) - nsi[1];"
    NewCode += "\n           mat[1][0] = ((nor[0] * nor[1]) * ico) - nsi[2];"
    NewCode += "\n           mat[1][1] = ((nor[1] * nor[1]) * ico) + co;"
    NewCode += "\n           mat[1][2] = ((nor[1] * nor[2]) * ico) + nsi[0];"
    NewCode += "\n           mat[2][0] = ((nor[0] * nor[2]) * ico) + nsi[1];"
    NewCode += "\n           mat[2][1] = ((nor[1] * nor[2]) * ico) - nsi[0];"
    NewCode += "\n           mat[2][2] = ((nor[2] * nor[2]) * ico) + co;"
    NewCode += "\n       }*/"
    NewCode += "\n        float3 rgb2hsv(float3 c)"
    NewCode += "\n        {"
    NewCode += "\n            float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);"
    NewCode += "\n            float4 p = lerp(float4(c.bg, K.wz), float4(c.gb, K.xy), step(c.b, c.g));"
    NewCode += "\n            float4 q = lerp(float4(p.xyw, c.r), float4(c.r, p.yzx), step(p.x, c.r));"
    NewCode += "\n            "
    NewCode += "\n            float d = q.x - min(q.w, q.y);"
    NewCode += "\n            float e = 1.0e-10;"
    NewCode += "\n            return float3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);"
    NewCode += "\n        }"
    NewCode += "\n        float noise(int n) /* fast integer noise (taken from https://github.com/blender/blender/blob/master/source/blender/nodes/texture/nodes/node_texture_bricks.c  This was to try to implement noise or brick textures) */"
    NewCode += "\n        {"
    NewCode += "\n            int nn;"
    NewCode += "\n            n = (n / 24) ^ n;"
    NewCode += "\n            nn = (n * (n * n * 60493 + 19990303) + 1376312589);"
    NewCode += "\n            return 0.5 * (nn / 1073741824.0);"
    NewCode += "\n        }"
    NewCode += "\n        "
    NewCode += globals #put in global varibles
    NewCode += "\n        "
    NewCode += "\n        // Add instancing support for this shader. You need to check 'Enable Instancing' on materials that use the shader."
    NewCode += "\n        // See https://docs.unity3d.com/Manual/GPUInstancing.html for more information about instancing."
    NewCode += "\n        // #pragma instancing_options assumeuniformscaling"
    NewCode += "\n        UNITY_INSTANCING_BUFFER_START(Props)"
    NewCode += "\n             // put more per-instance properties here"
    NewCode += "\n        UNITY_INSTANCING_BUFFER_END(Props)"
    NewCode += "\n        "
    NewCode += "\n        void surf (Input IN, inout SurfaceOutputStandard o)"
    NewCode += "\n        {"
    NewCode += "\n            float fresnel = dot(IN.worldNormal, IN.viewDir);"
    NewCode += "\n            float shadow = 0;"
    NewCode += "\n            float4 placeholder = tex2D(_"+bpy.context.scene.BlToUnShader_uvtex+", IN.uv_"+bpy.context.scene.BlToUnShader_uvtex+");"
    NewCode += locals #declare local varibles for later use
    
    #sort the graph so it has the correct order.
    #this uses a topology sort, so the operations in unity are done in the right order.
    SortedNodes = sortNodes(material)
    
    #iterate through all the nodes and their inputs to make Class objects of each node.
    for node in SortedNodes:
        
        #check if the node is supported before anything else.
        if(node.type in unsupported):
            writedebug(node.type + " with the name "+node.label+" is unsupported and possibly Blender 3D only!  I would give you a gold star to implement this one!")
            continue
        
        nodeInputTypes = []
        for link in node.inputs:
            
                
            if(node.type == "BUMP"):
                    if(link.name == "Height_dx" or link.name == "Height_dy"):
                        continue
            
            inputchild = link
            if(len(inputchild.links) == 0):
                outputparent = inputchild
                
                if(inputchild.type == "RGBA"):
                    nodeInputTypes.append("\"float4("+str(inputchild.default_value[0])+","+str(inputchild.default_value[1])+","+str(inputchild.default_value[2])+","+str(inputchild.default_value[3])+")\"")
                elif(inputchild.type == "VALUE"):
                    averagevalue = inputchild.default_value
                    nodeInputTypes.append("\"float4("+str(averagevalue)+","+str(averagevalue)+","+str(averagevalue)+","+str(averagevalue)+")\"")
                elif(inputchild.type == "SHADER"):
                    nodeInputTypes.append("[\"float4(0.0,0.0,0.0,0.0)\",True]");
                elif(inputchild.type == "VECTOR"):
                    nodeInputTypes.append("\"float4("+str(inputchild.default_value[0])+","+str(inputchild.default_value[1])+","+str(inputchild.default_value[2])+","+"1.0"+")\"")
                else:
                    writedebug("\nConnection error: \"Has No Connection\" input type \""+inputchild.type+"\" not implemented!")
            else:
                outputparent = link.links[0].from_socket
                
                
                
                #find outputparent index
                outputindex = 0
                for output, i in enumerate(outputparent.node.outputs):
                    if(i == outputparent):
                        outputindex = output
                
                
                #Figure out data node and convert
                if(inputchild.type == "RGBA" or inputchild.type == "IMAGE"):
                    nodeInputTypes.append("\""+outputparent.node.label+"["+str(outputindex)+"]"+"\"")
                elif(inputchild.type == "VALUE" and (outputparent.type == "VECTOR" or outputparent.type == "RGBA" or outputparent.type == "IMAGE")):
                    averagevalue = "(("+outputparent.node.label+"["+str(outputindex)+"].x"+"+"+outputparent.node.label+"["+str(outputindex)+"].y"+"+"+outputparent.node.label+"["+str(outputindex)+"].z)/3)"
                    nodeInputTypes.append("\"float4("+averagevalue+","+averagevalue+","+averagevalue+","+averagevalue+")\"")
                elif(outputparent.type == "VALUE" and (inputchild.type == "VECTOR" or inputchild.type == "RGBA" or inputchild.type == "IMAGE")):
                    averagevalue = outputparent.node.label+"["+str(outputindex)+"].r"
                    nodeInputTypes.append("\"float4("+averagevalue+","+averagevalue+","+averagevalue+","+averagevalue+")\"")
                elif(inputchild.type == "SHADER" and outputparent.type == "SHADER"):
                    nodeInputTypes.append("[\""+outputparent.node.label+"\",False]")
                elif(inputchild.type == "SHADER" and outputparent.type == "RGBA"):
                    nodeInputTypes.append("[\""+"float4("+outputparent.node.label+"["+str(outputindex)+"].r,"+outputparent.node.label+"["+str(outputindex)+"].g,"+outputparent.node.label+"["+str(outputindex)+"].b,"+outputparent.node.label+"["+str(outputindex)+"].a)"+"\",True]")
                elif((inputchild.type == "RGBA" and outputparent.type == "VECTOR") or (inputchild.type == "VECTOR" and outputparent.type == "RGBA")):
                    nodeInputTypes.append("\""+outputparent.node.label+"["+str(outputindex)+"]"+"\"")
                elif(inputchild.type == "VECTOR" and outputparent.type == "VECTOR"):
                    nodeInputTypes.append("\""+outputparent.node.label+"["+str(outputindex)+"]"+"\"")
                elif(inputchild.type == "VALUE" and outputparent.type == "VALUE"):
                    averagevalue = outputparent.node.label+"["+str(outputindex)+"].r"
                    nodeInputTypes.append("\"float4("+str(averagevalue)+","+str(averagevalue)+","+str(averagevalue)+","+str(averagevalue)+")\"")
                else:
                    writedebug("\nConnection error: \"Has Connection\" type "+inputchild.type+" ---> "+outputparent.type+" not implemented!")
        
        
        
        executeString = ""+node.type+"(\""+node.label+"\""
        
        for input in nodeInputTypes:
            executeString += ","+input
        
        #FOR NODE PROPERTIES
        if(node.type == "BSDF_GLASS" or node.type == "BSDF_GLOSSY" or node.type == "BSDF_PRINCIPLED"):
            executeString += ",\""+node.distribution+"\""
        elif(node.type == "MATH"):
            
            
            if(node.operation in ["SQRT", "EXPONENT", "SIGN", "ROUND", "FLOOR", "CEIL", "TRUNC", "FRACT", "SINE", "COSINE", "TANGENT", "ARCSINE", "ARCCOSINE", "ARCTANGENT", "SINH", "COSH", "TANH", "RADIANS", "DEGREES" ]):
                executeString += ",\"float4(1.0,1.0,1.0,1.0)\""
                executeString += ",\"float4(1.0,1.0,1.0,1.0)\""
                executeString += ","+str(node.use_clamp)+",\""+node.operation+"\""
            elif(node.operation in ["MULTIPLY_ADD", "COMPARE","SMOOTH_MIN", "SMOOTH_MAX", "WRAP"]):
                executeString += ","+str(node.use_clamp)+",\""+node.operation+"\""
            else:
                executeString += ","+str(node.use_clamp)+",\""+node.operation+"\""
                
                
        elif(node.type == "RGB"):
            executeString = "RGB(\""+node.label+"\",["+str(node.outputs[0].default_value[0])+","+str(node.outputs[0].default_value[1])+","+str(node.outputs[0].default_value[2])+","+str(node.outputs[0].default_value[3])+"]"
        elif(node.type == "TEX_BRICK"):
            executeString += ","+"\""+float4ify(str(node.offset))+"\""+","+"\""+float4ify(str(node.offset_frequency))+"\""+","+"\""+float4ify(str(node.squash))+"\""+","+"\""+float4ify(str(node.squash_frequency))+"\""
        elif(node.type == "TEX_GRADIENT"):
            executeString += ",\""+node.gradient_type+"\""
        elif(node.type == "TEX_MAGIC"):
            executeString += ","+"\""+float4ify(str(node.turbulence_depth))+"\""
        elif(node.type == "TEX_MUSGRAVE"):
            #refrence code comment
            # name, vector, W, scale, detail, dimension, lacunarity, offset, gain, mode, dimspace
            executeString += ","+"\""+node.musgrave_type+"\",\""+node.musgrave_dimensions+"\""
        elif(node.type == "TEX_NOISE"):
            executeString += ","+"\""+node.noise_dimensions+"\""
        elif(node.type == "TEX_POINTDENSITY"):
            if(node.point_source == "PARTICLE_SYSTEM"):
                executeString += ","+"\""+node.point_source+"\""+",node.object,"+"\""+node.space+"\""+","+"\""+float4ify(str(node.radius))+"\""+","+"\""+node.interpolation+"\""+","+"\""+float4ify(str(node.resolution))+"\""+","+"\""+node.particle_color_source+"\""
                    
                
            elif(node.point_source == "OBJECT"):
                executeString += ","+"\""+node.point_source+"\""+",node.object,"+"\""+node.space+"\""+","+"\""+float4ify(str(node.radius))+"\""+","+"\""+node.interpolation+"\""+","+"\""+float4ify(str(node.resolution))+"\""+","+"\""+node.vertex_color_source+"\""
        elif(node.type == "TEX_SKY"):
            #refrence code comment for less scrolling \/
            #name, vector, turbidity, groundalbedo, sunsize, sunintensity, sunelevation, sunrotation, altitude, air, dust, ozone, mode
            if(node.sky_type == "PREETHAM"):
                executeString += ","+"\""+float4ify(""+node.turbidity)+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+node.sky_type+"\""
            elif(node.sky_type == "HOSEK_WILKIE"):
                executeString += ","+"\""+float4ify(""+node.turbidity)+"\""+","+"\""+float4ify(""+node.ground_albedo)+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+node.sky_type+"\""
            elif(node.sky_type == "NISHITA"):
                executeString += ","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify(str(node.sun_size))+"\""+","+"\""+float4ify(str(node.sun_intensity))+"\""+","+"\""+float4ify(str(node.sun_elevation))+"\""+","+"\""+float4ify(str(node.sun_rotation))+"\""+","+"\""+float4ify(str(node.altitude))+"\""+","+"\""+float4ify(str(node.air_density))+"\""+","+"\""+float4ify(str(node.dust_density))+"\""+","+"\""+float4ify(str(node.ozone_density))+"\""+","+"\""+node.sky_type+"\""
        elif(node.type == "TEX_VORONOI"):
            #heh, this was advanced but I did it and made incoming varible number consistent for the 
            #refrence input comment for less scrolling \/
            #name, vector, W, scale, smoothness, exponent, randomness, dimension, feature, distance
            
            executeString = ""+node.type+"(\""+node.label+"\"" #reset execute string. We wanna handle this one ourselves.
            
            
            #array that supplies pure 1.0 float4's based on what mode the node is on. Inputs that don't exist on the node with the current settings are just set to 1.0
            #the array's first index is dimension. Next is distance, and last is feature. Sometimes a certain dimension doesn't support features so that last index won't exist. 
            #The array then has an array of strings at the 3rd set of [], which is then assembled with "," joining them, making a list that fits the inputs for the function every time.
            
            voronoiCorrectionArray = [
                [# 1D
                    ["\""+float4ify("1.0")+"\"", nodeInputTypes[0], nodeInputTypes[1], "\""+float4ify("1.0")+"\"", "\""+float4ify("1.0")+"\"", nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\"\"", "\""+node.distance+"\""],#f1
                    ["\""+float4ify("1.0")+"\"", nodeInputTypes[0], nodeInputTypes[1], "\""+float4ify("1.0")+"\"", "\""+float4ify("1.0")+"\"", nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\"\"", "\""+node.distance+"\""],#f2
                    ["\""+float4ify("1.0")+"\"", nodeInputTypes[0], nodeInputTypes[1], nodeInputTypes[2], "\""+float4ify("1.0")+"\"", nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\"\"", "\""+node.distance+"\""],#smooth f1
                    ["\""+float4ify("1.0")+"\"", nodeInputTypes[0], nodeInputTypes[1], "\""+float4ify("1.0")+"\"", "\""+float4ify("1.0")+"\"", nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\"\"", "\""+node.distance+"\""],#distance to edge
                    ["\""+float4ify("1.0")+"\"", nodeInputTypes[0], nodeInputTypes[1], "\""+float4ify("1.0")+"\"", "\""+float4ify("1.0")+"\"", nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\"\"", "\""+node.distance+"\""] #N-sphere radius
                ],
                [# 2D
                    [#F1
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"",nodeInputTypes[2],nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [#F2
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"",nodeInputTypes[2],nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [#Smooth F1
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],nodeInputTypes[2],nodeInputTypes[3],nodeInputTypes[4], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],#Distance to edge
                    [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""] #N-sphere radius
                ],
                [#3D
                    [#F1
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"",nodeInputTypes[2],nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [#F2
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"",nodeInputTypes[2],nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [#Smooth F1
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],nodeInputTypes[2],nodeInputTypes[3],nodeInputTypes[4], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],#Distance to edge
                    [nodeInputTypes[0],"\""+float4ify("1.0")+"\"",nodeInputTypes[1],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[2], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""] #N-sphere radius
                ],
                [# 4D
                    [#F1
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"",nodeInputTypes[3],nodeInputTypes[4], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [#F2
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"",nodeInputTypes[3],nodeInputTypes[4], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [#Smooth F1
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],nodeInputTypes[3],"\""+float4ify("1.0")+"\"",nodeInputTypes[4], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],nodeInputTypes[3],"\""+float4ify("1.0")+"\"",nodeInputTypes[4], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],nodeInputTypes[3],"\""+float4ify("1.0")+"\"",nodeInputTypes[4], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],
                        [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],nodeInputTypes[3],nodeInputTypes[4],nodeInputTypes[5], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""]
                    ],
                    [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""],#Distance to edge
                    [nodeInputTypes[0],nodeInputTypes[1],nodeInputTypes[2],"\""+float4ify("1.0")+"\"","\""+float4ify("1.0")+"\"",nodeInputTypes[3], "\""+node.voronoi_dimensions+"\"", "\""+node.feature+"\"", "\""+node.distance+"\""] #N-sphere radius
                ]
            ]
            
            
            
            part1 = voronoiCorrectionArray[["1D","2D","3D","4D"].index(node.voronoi_dimensions)]
            
            part2 = []
            
            if(node.feature in ["F1","F2","SMOOTH_F1"]):
                part2 = part1[["F1","F2","SMOOTH_F1"].index(node.feature+"")][["EUCLIDEAN", "MANHATTAN", "CHEBYCHEV", "MINKOWSKI"].index(node.distance+"")]
            else:
                part2 = part1[["DISTANCE_TO_EDGE","N_SPHERE_RADIUS"].index(node.feature+"")+3]
            
            for string in part2:
                executeString += ","+string
            
            
        elif(node.type == "TEX_ENVIRONMENT" or node.type == "TEX_IMAGE"):
            if(node.image):
                executeString += ",\""+node.image.name+"\""
            else:
                executeString += ",\""+"\""
        elif(node.type == "TEX_WAVE"):
            executeString += ",\""+node.wave_type+"\",\""+node.rings_direction+"\",\""+node.wave_profile+"\""
        elif(node.type == "VECT_MATH"):
            executeString = ""+node.type+"(\""+node.label+"\""
            executeString += ", nodeInputTypes "+",\""+node.operation+"\""
        elif(node.type == "VECTOR_ROTATE"):
            #refrence inputs comment \/
            #(name, vector, center, axis, angle, rotation, mode, invert)
            if(node.rotation_type == "AXIS"):
                executeString = ""+node.type+"(\""+node.label+"\","+nodeInputTypes[0]+","+"\""+float4ify("1.0")+"\""+","+nodeInputTypes[1]+","+nodeInputTypes[2]+","+"\""+float4ify("1.0")+"\""+",\""+node.rotation_type+"\","+str(node.invert)
            elif(node.rotation_type == "EULER_XYZ"):
                executeString = ""+node.type+"(\""+node.label+"\","+nodeInputTypes[0]+","+nodeInputTypes[1]+","+"\""+float4ify("1.0")+"\""+","+"\""+float4ify("1.0")+"\""+","+nodeInputTypes[2]+",\""+node.rotation_type+"\","+str(node.invert)
            elif(node.rotation_type == "X_AXIS" or node.rotation_type == "Y_AXIS" or node.rotation_type == "Z_AXIS"):
                executeString = ""+node.type+"(\""+node.label+"\","+nodeInputTypes[0]+","+nodeInputTypes[1]+","+"\""+float4ify("1.0")+"\""+","+nodeInputTypes[2]+","+"\""+float4ify("1.0")+"\""+",\""+node.rotation_type+"\","+str(node.invert)
            else:
                writedebug("\nsomething weird happened with VECTOR_ROTATE name:\""+node.label+"\" What did you do!?!")
        elif(node.type == "WIREFRAME"):
            executeString += ",\""+str(node.use_pixel_size)+"\""
        elif(node.type == "MAPPING"):
            #refrence inputs for less scrolling \/
            # name,vector,location, rotation, scale, mode
            if(node.vector_type == "POINT"):
                executeString += "\"node.vector_type\""
            elif(node.vector_type == "TEXTURE"):
                executeString += "\"node.vector_type\""
            elif(node.vector_type == "VECTOR"):
                executeString = ""+node.type+"(\""+node.label+"\""
                executeString += ","+nodeInputTypes[0]+","+"\""+float4ify("1.0")+"\""+","+nodeInputTypes[0]+","+nodeInputTypes[0]+",\""+node.vector_type+"\""
            elif(node.vector_type == "NORMAL"):
                executeString = ""+node.type+"(\""+node.label+"\""
                executeString += ","+nodeInputTypes[0]+","+"\""+float4ify("1.0")+"\""+","+nodeInputTypes[0]+","+nodeInputTypes[0]+",\""+node.vector_type+"\""
        elif(node.type == "MIX_RGB"):
            executeString += ",\""+node.blend_type+"\""
        elif(node.type == "CLAMP"):
            executeString += ",\""+node.clamp_type+"\""
        elif(node.type == "VALTORGB"):
            executeString += ",node.color_ramp"
        elif(node.type == "VECT_TRANSFORM"):
            executeString += ",node.convert_from,node.convert_to"
        
        
        executeString += ")"
        
        writedebug("\nExecute String: "+executeString)
        
        NewCode += "\n            "+eval(executeString)
        
        if(bpy.context.scene.BlToUnShader_debugmode == True):
            NewCode += "// Type: \""+node.type+"\""
    
    #end the code
    #TO DO: Fix the metallic and smoothness being auto set
    
    NewCode +="\n        }"
    NewCode +="\n        ENDCG"
    NewCode +="\n    }"
    NewCode +="\n    FallBack \"Diffuse\""
    NewCode +="\n}"
    
    
    
    return NewCode


#so I (@989onan) can write less.
def float4ify(value):
    return "float4("+value+","+value+","+value+","+value+")"

def defineVarible(name, number):
    return "float4 "+name+"["+str(number)+"];"


##START NODE TYPES
##START NODE TYPES
##START NODE TYPES

def ADD_SHADER(name,input_shader1,input_shader2):
    
    start = ""
    
    if(not input_shader1[1]):
        input_shader1 = input_shader1[0]
    else:
        start += "float4 "+name+"_shader1_color = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader1_emission = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader1_roughness = "+float4ify("1.0")+";\n            "
        input_shader1 = name+"_shader1"
    if(not input_shader2[1]):
        input_shader2 = input_shader2[0]
    else:
        start += "float4 "+name+"_shader2_color = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader2_emission = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader2_roughness = "+float4ify("1.0")+";\n            "
        input_shader2 = name+"_shader2"
    
    return start+name+"_color = "+input_shader1+"_color + "+input_shader2+"_color;\n            "+name+"_emission = "+input_shader1+"_emission + "+input_shader2+"_emission;\n            "+name+"_roughness = "+input_shader1+"_roughness + "+input_shader2+"_roughness;"
def define_ADD_SHADER(name):
    return ["float4 "+name+"_color;"+"\n            float4 "+name+"_emission;"+"\n            float4 "+name+"_roughness;","",""]


def BRIGHTCONTRAST(name,color,bright,contrast):
    return name+"[0] = "+contrast+"*("+color+"-float4(128.0,128.0,128.0,0.5))"+"+float4(128.0,128.0,128.0,0.5)+"+bright+";"
def define_BRIGHTCONTRAST(name):
    return [defineVarible(name,1),"",""]


def BSDF_DIFFUSE(name,color,roughness,normal):
    return name+"_color = "+color+";\n            "+name+"_emission = float4(0.0,0.0,0.0,0.0);\n            "+name+"_roughness = float4(1.0,1.0,1.0,1.0);"
def define_BSDF_DIFFUSE(name):
    return ["float4 "+name+"_color;"+"\n            float4 "+name+"_emission;"+"\n            float4 "+name+"_roughness;","",""]


def BSDF_GLASS(name,color,roughness,IOR,normal,mode):
    if(mode == "SHARP"):
        return name+"_color = float4("+color+".r,"+color+".g,"+color+".b,"+"0);\n            "+name+"_emission = float4(0,0,0,0);\n            "+name+"_roughness = float4(0.0,0.0,0.0,1.0);"
    else:    
        return name+"_color = float4("+color+".r,"+color+".g,"+color+".b,"+"0);\n            "+name+"_emission = float4(0,0,0,0);\n            "+name+"_roughness = "+roughness+";"
def define_BSDF_GLASS(name):
    return ["float4 "+name+"_color;"+"\n            float4 "+name+"_emission;"+"\n            float4 "+name+"_roughness;","",""]


def BSDF_GLOSSY(name,color,roughness,normal,mode):
    if(mode == "SHARP"):
        return name+"_color = "+color+";\n            "+name+"_emission = float4(0,0,0,0);\n            "+name+"_roughness = float4(0.0,0.0,0.0,1.0);"
    else:
        return name+"_color = "+color+";\n            "+name+"_emission = float4(0,0,0,0);\n            "+name+"_roughness = "+roughness+";"
def define_BSDF_GLOSSY(name):
    return ["float4 "+name+"_color;"+"\n            float4 "+name+"_emission;"+"\n            float4 "+name+"_roughness;","",""]


def BSDF_PRINCIPLED(name,color,subsurface,subsurfaceRadius,subsurfaceColor,metallic,specular,specularTint,roughness,anisotropic,anisotropicRotation,sheen,sheenTint,clearcoat,clearcoatRoughness,IOR,transmission,transmissionRoughness,emission,emissionStrength,alpha,normal,clearcoatNormal,tangent,mode):
    if(mode == "SHARP"):
        return "//BSDF principle nodes are very barebones in this tool and are missing many features! please consider replacing this node. \n            //For now, every varible with \""+name+"\" in the name and everything after it is a barebones implementation/patch! \n            "+name+"_color = float4("+color+".r,"+color+".g,"+color+".b,"+alpha+".a"+");\n            "+name+"_emission = "+emission+" * "+emissionStrength+";\n            "+name+"_roughness = float4(0.0,0.0,0.0,1.0);"
    else:
        return "//BSDF principle nodes are very barebones in this tool and are missing many features! please consider replacing this node. \n            //For now, every varible with \""+name+"\" in the name and everything after it is a barebones implementation/patch! \n            "+name+"_color = float4("+color+".r,"+color+".g,"+color+".b,"+alpha+".a"+");\n            "+name+"_emission = "+emission+" * "+emissionStrength+";\n            "+name+"_roughness = "+roughness+";"
def define_BSDF_PRINCIPLED(name):
    return ["float4 "+name+"_color;"+"\n            float4 "+name+"_emission;"+"\n            float4 "+name+"_roughness;","",""]


def BSDF_TRANSPARENT(name,color):
    return name+"_color = "+color+";\n            "+name+"_roughness = float4(1.0,1.0,1.0,1.0);"+"\n            "+name+"_emission = "+"float4(0.0,0.0,0.0,0.0);"
def define_BSDF_TRANSPARENT(name):
    return ["float4 "+name+"_color;"+"\n            float4 "+name+"_emission;"+"\n            float4 "+name+"_roughness;","",""]


def BUMP(name, strength, distance, height, normal):
    return "//This node ("+name+") is not... quite there yet. Here, have a placeholder that should do the job!\n            "+name+"[0] = ("+strength+" * "+distance+") + "+height+";"
def define_BUMP(name):
    return [defineVarible(name,1),"",""]


def CAMERA(name):
    return "//This node ("+name+") I don't quite understand. Here is something that might do it.\n            "+name+"[0] = float4(IN.viewDir.x,IN.viewDir.y,IN.viewDir.z,1.0);\n            "+name+"[1] = "+float4ify("distance(IN.worldPos, _WorldSpaceCameraPos)")+";"+"\n            "+name+"[2] = "+float4ify("distance(IN.worldPos, _WorldSpaceCameraPos)")+";"
def define_CAMERA(name):
    return [defineVarible(name,3),"",""]


#no need for mode settings I believe
def CLAMP(name, value, min, max, mode):
    clamp = "clamp("+value+".r,"+min+".r,"+max+".r)"
    return name+"[0] = float4("+clamp+","+clamp+","+clamp+","+clamp+");"
def define_CLAMP(name):
    return [defineVarible(name,1),"",""]


def COMBHSV(name, h,s,v):
    return name+"[0] = float4(hsv2rgb(float3("+h+".r,"+s+".r,"+v+".r)),1.0);"
def define_COMBHSV(name):
    return [defineVarible(name,1),"",""]


def COMBRGB(name, r,g,b):
    return name+"[0] = float4("+r+".r,"+g+".g,"+b+".b,1);"
def define_COMBRGB(name):
    return [defineVarible(name,1),"",""]


def COMBXYZ(name,x,y,z):
    return name+"[0] = float4("+x+".r,"+y+".g,"+z+".b,1);"
def define_COMBXYZ(name):
    return [defineVarible(name,1),"",""]


def EMISSION(name,color,strength):
    return name+"_color = float4("+color+".r,"+color+".g,"+color+".b,1);\n            "+name+"_emission = float4("+color+".r,"+color+".g,"+color +".b,1) * "+strength+".r;\n            "+name+"_roughness =  float4(1,1,1,1) * "+strength+".r;"
def define_EMISSION(name):
    return ["float4 "+name+"_color;"+"\n            float4 "+name+"_emission;"+"\n            float4 "+name+"_roughness;","",""]


def FRESNEL(name,IOR, normal):
    return  "//This node ("+name+") I don't quite understand. Here is something that might do it.\n            "+name+"[0] = float4(fresnel,fresnel,fresnel,fresnel);"
def define_FRESNEL(name):
    return [defineVarible(name,1),"",""]


def GAMMA(name, color, gamma):
    return name+"[0] = float4(pow("+color+".r,"+gamma+".r),pow("+color+".r,"+gamma+".r),pow("+color+".r,"+gamma+".r),pow("+color+".r,"+gamma+".r));"
def define_GAMMA(name):
    return [defineVarible(name,1),"",""]


def HUE_SAT(name, hue, saturation, value, factor, color):
    return name+"[0] = lerp("+color+",float4("+"rgb2hsv(float3("+color+".r,"+color+".g,"+color+".b)).r,"+"rgb2hsv(float3("+color+".r,"+color+".g,"+color+".b)).g,"+"rgb2hsv(float3("+color+".r,"+color+".g,"+color+".b)).b,"+color+".a),"+factor+".r);"
def define_HUE_SAT(name):
    return [defineVarible(name,1),"",""]


def INVERT(name, factor,color):
    lerp = "lerp("+color+",(1-"+color+"),"+factor+".r)"
    return name+"[0] = float4("+lerp+".r,"+lerp+".g,"+lerp+".b,"+lerp+".a);"
def define_INVERT(name):
    return [defineVarible(name,1),"",""]


def LAYER_WEIGHT(name,blend,normal):
    return  "//This node ("+name+") I don't quite understand. Here is something that might do it.\n            "+name+"[0] = float4(fresnel,fresnel,fresnel,fresnel);\n            "+name+"[1] = float4(fresnel,fresnel,fresnel,fresnel);"
def define_LAYER_WEIGHT(name):
    return [defineVarible(name,2),"",""]


#camdist = "distance(IN.worldPos, _WorldSpaceCameraPos)" #maybe use in another node?

#Note: Try to fix this.
def MAP_RANGE(name,value,from_min,from_max,to_min,to_max, mode):
    result = "("+to_min+".r + (("+value+".r - "+from_min+".r)/("+from_max+".r - "+from_min+".r)) * ("+to_max+".r - "+to_min+".r))"
    if(mode == "LINEAR"):
        return name+"[0] = "+float4ify(result)+";"
    else:
        return "//I have no idea what to do on a case other than linear. Here's Linear instead.\n            "+name+"[0] = "+float4ify(result)+";"
def define_MAP_RANGE(name):
    return [defineVarible(name,1),"",""]


#FINISH THIS!!!
#IMPLEMENT MODE SETTINGS
def MAPPING(name,vector,location, rotation, scale, mode):
    return name+"[0] = "+float4ify("1.0")+";"
def define_MAPPING(name):
    return [defineVarible(name,1),"",""]


#FINISH IMPLEMENTING MODE SETTINGS
def MATH(name, value1, value2, value3, clamp, math):
    
    value1 = value1+".r"
    value2 = value2+".r"
    value3 = value3+".r"
    equa = name+"[0] = "
    
    final = ""
    
    #haha, Optimization be like: if else if else if else if else if else if else - @989onan
    
    if(math == "ADD"):
        final = "("+value1+"+"+value2+")"
    elif(math == "SUBTRACT"):
        final = "("+value1+"-"+value2+")"
    elif(math == "MULTIPLY"):
        final = "("+value1+"*"+value2+")"
    elif(math == "DIVIDE"):
        final = "("+value1+"/"+value2+")"
    elif(math == "MULTIPLY_ADD"):
        final = "(("+value1+"*"+value2+")+"+value3+")"
    elif(math == "POWER"):
        final = "(pow("+value1+","+value2+"))"
    elif(math == "LOGARITHM"):
        final = "(log("+value1+")/log("+value2+"))"
    elif(math == "SQRT"):
        final = "(pow("+value1+",0.5))"
    elif(math == "INVERSE_SQRT"):
        final = "(1/pow("+value1+",0.5))"
    elif(math == "ABSOLUTE"):
        final = "(abs("+value1+"))"
    elif(math == "EXPONENT"):
        final = "(exp("+value1+"))"
    elif(math == "MINIMUM"):
        final = "(min("+value1+","+value2+"))"
    elif(math == "MAXIMUM"):
        final = "(max("+value1+","+value2+"))"
    elif(math == "LESS_THAN"):
        final = "(A < B ? 1 : 0)"
    elif(math == "GREATER_THAN"):
        final = "(A > B ? 1 : 0)"
    elif(math == "SIGN"):
        final = "(sign("+value1+"))"
    elif(math == "COMPARE"):
        return "//Woops! Not a coded math type! (type: \""+math+"\") Here's a placeholder."+"\n            "+MathHelper(equa, "1.0") #untiy has this for exact comparison. Someone adapt this: "A == B ? 1 : 0" 
    elif(math == "SMOOTH_MIN"):
        return "//Woops! Not a coded math type! (type: \""+math+"\") Here's a placeholder."+"\n            "+MathHelper(equa, "1.0")
    elif(math == "SMOOTH_MAX"):
        return "//Woops! Not a coded math type! (type: \""+math+"\") Here's a placeholder."+"\n            "+MathHelper(equa, "1.0")
    elif(math == "ROUND"):
        final = "(round("+value1+"))"
    elif(math == "FLOOR"):
        final = "(floor("+value1+"))"
    elif(math == "CEIL"):
        final = "(ceil("+value1+"))"
    elif(math == "TRUNC"):
        final = "(trunc("+value1+"))"
    elif(math == "FRACT"):
        final = "(frac("+value1+"))"
    elif(math == "MODULO"):
        final = "(fmod("+value1+","+value2+"))"
    elif(math == "WRAP"):
        return "//Woops! Not a coded math type! (type: \""+math+"\") Here's a placeholder."+"\n            "+MathHelper(equa, "1.0")
    elif(math == "SNAP"):
        return "//Woops! Not a coded math type! (type: \""+math+"\") Here's a placeholder."+"\n            "+MathHelper(equa, "1.0")
    elif(math == "PINGPONG"):
        return "//Woops! Not a coded math type! (type: \""+math+"\") Here's a placeholder."+"\n            "+MathHelper(equa, "1.0")
    elif(math == "SINE"):
        final = "(sin("+value1+"))"
    elif(math == "COSINE"):
        final = "(cos("+value1+"))"
    elif(math == "TANGENT"):
        final = "(tan("+value1+"))"
    elif(math == "ARCSINE"):
        final = "(asin("+value1+"))"
    elif(math == "ARCCOSINE"):
        final = "(acos("+value1+"))"
    elif(math == "ARCTANGENT"):
        final = "(atan("+value1+"))"
    elif(math == "ARCTAN2"):
        final = "(atan2("+value1+","+value2+"))"
    elif(math == "SINH"):
        final = "(sinh("+value1+"))"
    elif(math == "COSH"):
        final = "(cosh("+value1+"))"
    elif(math == "TANH"):
        final = "(tanh("+value1+"))"
    elif(math == "RADIANS"):
        final = "(("+value1+")* (3.141592653589793238462*180))"
    elif(math == "DEGREES"):
        final = "(("+value1+")* (3.141592653589793238462/180))"
    else:
        return "//Woops! Not a coded math type! (type: \""+math+"\") Here's a placeholder."+"\n            "+MathHelper(equa, "1.0")
    
    if(clamp == False):
        return MathHelper(equa,final)
    else:
        return MathHelper(equa,"saturate("+final+")")
    
    ##CONTINUE TYPES!!!
def MathHelper(equa,value):
    return equa+"float4("+value+","+value+","+value+","+value+");"    
def define_MATH(name):
    return [defineVarible(name,1),"",""]

#IMPLEMENT MODE SETTINGS
def MIX_RGB(name, factor, color1, color2, mixmode):
    if(mixmode == "MIX"):
        return name+"[0] = lerp("+color1+","+color2+","+factor+".r);"
def define_MIX_RGB(name):
    return [defineVarible(name,1),"",""]


def MIX_SHADER(name, factor, shader1, shader2):
    
    start = ""
    
    if(not shader1[1]):
        shader1 = shader1[0]
    else:
        start += "float4 "+name+"_shader1_color = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader1_emission = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader1_roughness = "+float4ify("1.0")+";\n            "
        shader1 = name+"_shader1"
    if(not shader2[1]):
        shader2 = shader2[0]
    else:
        start += "float4 "+name+"_shader2_color = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader2_emission = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader2_roughness = "+float4ify("1.0")+";\n            "
        shader2 = name+"_shader2"
    
    
    return start+name+"_color = lerp("+shader1+"_color,"+shader2+"_color,"+factor+".r);\n            "+name+"_emission = lerp("+shader1+"_emission,"+shader2+"_emission,"+factor+".r);\n            "+name+"_roughness = lerp("+shader1+"_roughness,"+shader2+"_roughness,"+factor+".r);"
def define_MIX_SHADER(name):
    return ["float4 "+name+"_color;"+"\n            float4 "+name+"_emission;"+"\n            float4 "+name+"_roughness;","",""]


def OBJECT_INFO(name):
    return name+"[0] = IN.worldPos;\n            //Everything below that refrences "+name+"[1],"+name+"[2],"+name+"[3], and "+name+"[4] are just placeholders and don't do anything!\n            //They are probably the reason why your material doesn't work if they are refrenced!\n            "+name+"[1] = "+float4ify("1.0")+";\n            "+name+"[2] = "+float4ify("1.0")+";\n            "+name+"[3] = "+float4ify("1.0")+";\n            "+name+"[4] = "+float4ify("1.0")+";"
def define_OBJECT_INFO(name):
    return [defineVarible(name,5),"",""]


def OUTPUT_MATERIAL(name,shader1,volume,displacement):
    
    
    if(not shader1[1]):
        shader1 = shader1[0]
        return "o.Albedo = "+shader1+"_color.rgb;\n            o.Alpha = "+shader1+"_color.a;\n            o.Emission = "+shader1+"_emission.rgb;\n            o.Smoothness = abs("+shader1+"_roughness.r-1);\n            o.Normal = "+displacement+".xyz;"
    else:
        shader1 = shader1[0]
        return "o.Albedo = "+shader1+".rgb;\n            o.Alpha = "+shader1+".a;\n            o.Emission = "+shader1+".rgb;\n            o.Smoothness = abs("+float4ify("0.0")+".r-1);\n            o.Normal = "+displacement+".xyz;"
    
def define_OUTPUT_MATERIAL(name):
    return ["","",""]


def RGB(name,color):
    return name+"[0] = float4("+str(color[0])+","+str(color[1])+","+str(color[2])+","+str(color[3])+");"
def define_RGB(name):
    return [defineVarible(name,1),"",""]


##IMPLEMENT!
def CURVE_RGB(name,factor,color):
    return "//This node (name: \""+name+"\") is yet to be implemented! This is a complicated node, so as the author (989onan) I have no clue how to implement this! Please find someone who can!\n            "+name+"[0] = "+float4ify("1.0")+";//placeholder so your shader compiles!"
def define_CURVE_RGB(name):
    return [defineVarible(name,1),"",""]


def RGBTOBW(name, color):
    return name+"[0] = float4("+color+".r,"+color+".g,"+color+".b,0.0);"
def define_RGBTOBW(name):
    return [defineVarible(name,1),"",""]


def SEPHSV(name,color):
    hsv = "rgb2hsv(float3("+color+".r,"+color+".g,"+color+".b))"
    return name+"[0] = float4("+hsv+".x,"+hsv+".x,"+hsv+".x,"+hsv+".x);\n            "+name+"[1] = float4("+hsv+".y,"+hsv+".y,"+hsv+".y,"+hsv+".y);\n            "+name+"[2] = float4("+hsv+".z,"+hsv+".z,"+hsv+".z,"+hsv+".z);"
def define_SEPHSV(name):
    return [defineVarible(name,3),"",""]


def SEPRGB(name, color):
    return name+"[0] = float4("+color+".r,"+color+".r,"+color+".r,"+color+".r);\n            "+name+"[1] = float4("+color+".g,"+color+".g,"+color+".g,"+color+".g);\n            "+name+"[2] = float4("+color+".b,"+color+".b,"+color+".b,"+color+".b);"
def define_SEPRGB(name):
    return [defineVarible(name,3),"",""]


def SEPXYZ(name, vector):
    hsv = vector
    return name+"[0] = float4("+hsv+".x,"+hsv+".x,"+hsv+".x,"+hsv+".x);\n            "+name+"[1] = float4("+hsv+".y,"+hsv+".y,"+hsv+".y,"+hsv+".y);\n            "+name+"[2] = float4("+hsv+".z,"+hsv+".z,"+hsv+".z,"+hsv+".z);"
def define_SEPXYZ(name):
    return [defineVarible(name,3),"",""]


##REVISIT!
def SHADERTORGB(name,shader):
    
    start = ""
    
    if(not shader[1]):
        shader = shader[0]
    else:
        start += "float4 "+name+"_shader_color = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader_emission = "+float4ify("0.0")+";\n            "
        start += "float4 "+name+"_shader_roughness = "+float4ify("1.0")+";\n            "
        shader = name+"_shader"
    
    
    return start+ "//This node (name: \""+name+"\") is yet to be implemented!\n            //This is due to the node needing a sample of the surface color of the shader that would show on the material surface when rendered. Here is a crappy patch instead...\n            "+name+"[0] = (("+shader+"_color * "+shader+"_emission) + ("+shader+"_roughness * "+float4ify("1.0")+"));\n            "+name+"[0] = "+shader+"_color.a;" ## We need a way to sample the cubemap with just shader code! ( replace "_roughness * float4(1.0,1.0,1.0,1.0));" with "_roughness * <Color of reflection map here>);" )
def define_SHADERTORGB(name):
    return [defineVarible(name,2),"",""]

##not sure if correct.
def SQUEEZE(name, value,width,center):
    return name+"[0] = 1.0 / (1.0 + pow(1, -(("+value+" - "+center+") * "+width+")));"
def define_SQUEEZE(name):
    return [defineVarible(name,1),"",""]


##IMPLEMENT!
def TEX_BRICK(name, vector, color1, color2, mortar, scale, mortarScale, mortarSmooth, bias, brickWidth, rowHeight, offset, offset_frequency, squash, squash_frequency):
    
    rownum = "("+scale+".r/"+rowHeight+".r)"
    
    
    altrowOffset = "(("+vector+".y * "+rownum+")%"+offset_frequency+".r)"
    altrowSquash = "(("+vector+".y * "+rownum+")%"+squash_frequency+".r)"
    
    
    brick_pattern_no_width = "(("+altrowOffset+"*"+offset+".r) + ("+altrowSquash+"*"+squash+".r))"
    
    
    
    return "//\"Node \'"+name+"\' type: \'TEX_BRICK\' is yet to be implemented! Here is a placeholder. Please find someone who can make the integer noise and the blender brick texture code. I went insane trying to do it.\" - @989onan"+"\n            "+name+"[0] = float4(1,1,1,1);"+"\n            "+name+"[1] = float4(1,1,1,1);"
def define_TEX_BRICK(name):
    return [defineVarible(name,2),"",""]


def TEX_CHECKER(name,vector,color1,color2,scale):
    
    lerp = "lerp("+color2+","+color1+",(abs(floor("+vector+".g*"+scale+".r)) + abs(floor("+vector+".r*"+scale+".r))) % 2)"
    
    final = name+"[0] = float4("+lerp+".r,"+lerp+".g,"+lerp+".b,"+lerp+".a);//Easier than most... - @989onan"
    final += "\n            "+name+"[1] = "+float4ify("lerp(0,1,(abs(floor("+vector+".r*"+scale+".r)) + abs(floor("+vector+".g*"+scale+".r))) % 2)")+"; //Easier than most... - @989onan"
    return final
def define_TEX_CHECKER(name):
    return [defineVarible(name,2),"",""]


def TEX_COORD(name):
    final = name+"[0] = "+float4ify("1.0")+";//anything that refrences this is broken."
    final += "\n            "+name+"[1] = float4(o.Normal.x,o.Normal.y,o.Normal.z,1.0);"
    final += "\n            "+name+"[2] = float4(IN.uv_"+bpy.context.scene.BlToUnShader_uvtex+".x,IN.uv_"+bpy.context.scene.BlToUnShader_uvtex+".y,0.0,1.0);"
    final += "\n            "+name+"[3] = "+float4ify("1.0")+";//anything that refrences this is broken."
    final += "\n            "+name+"[4] = IN.screenPos;"
    final += "\n            "+name+"[5] = IN.screenPos;"
    final += "\n            "+name+"[6] = float4(IN.worldRefl.x,IN.worldRefl.y,IN.worldRefl.z,1.0);//hope this needs world reflection. - @989onan"
    
    return final
def define_TEX_COORD(name):
    return [defineVarible(name,7),"",""]


def TEX_ENVIRONMENT(name, vector, imagename):
    if(imagename == ""):
        return name+"[0] = float4(1.0,0.0,1.0,1.0);"
    else:
        return name+"[0] = texCUBE(_"+name+"_Cube, IN.worldRefl);"
def define_TEX_ENVIRONMENT(name):
    return [defineVarible(name,1),"",""]


##IMPLEMENT!
def TEX_GRADIENT(name, vector, mode):
    return "//\"Node \'"+name+"\' type: \'TEX_GRADIENT\' is yet to be implemented! Here is a placeholder. I need someone who can implement this! - @989onan"+"\n            "+name+"[0] = "+float4ify("1.0")+";"+"\n            "+name+"[1] = "+float4ify("1.0")+";"
def define_TEX_GRADIENT(name):
    return [defineVarible(name,2),"",""]


def TEX_IMAGE(name, vector, imagename):
    if(imagename == ""):
        texture = "float4(1.0,0.0,1.0,1.0)"
    else:
        texture = "tex2D(_"+imagename+"_Texture,float2("+vector+".r,"+vector+".g))"
    return name+"[0] = float4("+texture+".r,"+texture+".g,"+texture+".b,1.0);\n            "+name+"[0] = "+float4ify(texture+".a")+";"
def define_TEX_IMAGE(name):
    return [defineVarible(name,2),"",""]


##IMPLEMENT!
def TEX_MAGIC(name,vector,scale,distortion,depth):
    return "//\"Node \'"+name+"\' type: \'TEX_MAGIC\' is yet to be implemented! Here is a placeholder. I need someone who can implement this! - @989onan"+"\n            "+name+"[0] = "+float4ify("1.0")+";"+"\n            "+name+"[1] = "+float4ify("1.0")+";"
def define_TEX_MAGIC(name):
    return [defineVarible(name,2),"",""]

##IMPLEMENT!
def TEX_MUSGRAVE(name, vector, W, scale, detail, dimension, lacunarity, offset, gain, mode, dimspace):
    return "//\"Node \'"+name+"\' type: \'TEX_MUSGRAVE\' is yet to be implemented! Here is a placeholder. I need someone who can implement this! - @989onan"+"\n            "+name+"[0] = "+float4ify("1.0")+";"
def define_TEX_MUSGRAVE(name):
    return [defineVarible(name,1),"",""]

##IMPLEMENT!
def TEX_NOISE(name, vector, W, scale, detail, roughness, distortion, dimension):
    return "//\"Node \'"+name+"\' type: \'TEX_MAGIC\' is yet to be implemented! Here is a placeholder. I need someone who can implement this! - @989onan"+"\n            "+name+"[0] = "+float4ify("1.0")+";"+"\n            "+name+"[1] = "+float4ify("1.0")+";"
def define_TEX_NOISE(name):
    return [defineVarible(name,2),"",""]

##IMPLEMENT!
#everything after vector are the internal settings in order from top to bottom. colorsource varible changes from "particle_color_source" and "vertex_color_source" according to which type is selected.
def TEX_POINTDENSITY(name, vector, type, object, space, radius, interpolation, resolution, colorsource):
    
    return "//\"Node \'"+name+"\' type: \'TEX_POINTDENSITY\' is yet to be implemented! Here is a placeholder. I need someone who can figure this one out. - @989onan "+"\n            "+name+"[0] = "+float4ify("1.0")+";"+"\n            "+name+"[1] = "+float4ify("1.0")+";"
def define_TEX_POINTDENSITY(name):
    return [defineVarible(name,2),"",""]


##IMPLEMENT!
#mode is the type of sky selected on the first dropdown menu. Every other varible will be set to float4(1.0,1.0,1.0,1.0) unless it is defined in the mode which that node is set to. so check the mode first to know if varibles are defined properly before handling them!
def TEX_SKY(name, vector, turbidity, groundalbedo, sunsize, sunintensity, sunelevation, sunrotation, altitude, air, dust, ozone, mode):
    return "//\"Node \'"+name+"\' type: \'TEX_SKY\' is yet to be implemented! Here is a placeholder. I need someone who can figure this one out. - @989onan "+"\n            "+name+"[0] = "+float4ify("1.0")+";"
def define_TEX_SKY(name):
    return [defineVarible(name,1),"",""]


##IMPLEMENT!
##inputs have been coded. dimension, feature, and distance varibles are the first 3 dropdown menus inside the node. 
def TEX_VORONOI(name, vector, W, scale, smoothness, exponent, randomness, dimension, feature, distance):
    return "//\"Node \'"+name+"\' type: \'TEX_VORONOI\' is yet to be implemented! Here is a placeholder. I need someone who can figure this one out. - @989onan "+"\n            "+name+"[0] = "+float4ify("1.0")+";"+"\n            "+name+"[1] = "+float4ify("1.0")+";"+"\n            "+name+"[2] = "+float4ify("1.0")+";"+"\n            "+name+"[3] = "+float4ify("1.0")+";"
def define_TEX_VORONOI(name):
    return [defineVarible(name,4),"",""] #never make node output amount vary please. That includes this node. That is for conistency - @989onan


def TEX_WAVE(name, vector, scale, distortion, detail, detailscale, detailroughness, phaseoffset, wave_type, rings_direction, wave_profile):
    
    #write some here to write less later (otherwise would have to write .toLowerCase() or something every time)
    if(rings_direction == "X"):
        rings_direction = "x"
    elif(rings_direction == "Y"):
        rings_direction = "y"
    elif(rings_direction == "Z"):
        rings_direction = "z"
    
    output = ""
    
    
    if(wave_profile == "SIN"):
        output = name+"[0] = sin("+vector+"."+rings_direction+");"+"\n            "+name+"[1] = sin("+vector+"."+rings_direction+");"
    elif(wave_profile == "SAW"):
        output = name+"[0] = 2 * ( - floor(0.5 + "+vector+"."+rings_direction+"));"+"\n            "+name+"[1] = 2 * ( - floor(0.5 + "+vector+"."+rings_direction+"));"
    elif(wave_profile == "TRI"):
        output = name+"[0] = 2.0 * abs( 2 * ("+vector+"."+rings_direction+" - floor(0.5 + "+vector+"."+rings_direction+")) ) - 1.0;"+"\n            "+name+"[1] = 2.0 * abs( 2 * ("+vector+"."+rings_direction+" - floor(0.5 + "+vector+"."+rings_direction+")) ) - 1.0;"
    
     
    return "//\"Node \'"+name+"\' type: \'TEX_WAVE\' is yet to be completely implemented! Here is a start on it. I need someone who can figure out the distortions and detail. - @989onan "+"\n            "+output
def define_TEX_WAVE(name):
    return [defineVarible(name,2),"",""]


def UVMAP(name):
    return "//\"Node \'"+name+"\' type: \'UVMAP\' can only be used for the first UV map since unity UV maps only technically supports one UV map and not multiple. Ask someone that knows Unity better. - @989onan"+name+"[0] = float4(uv_"+bpy.context.scene.BlToUnShader_uvtex+".x,uv_"+bpy.context.scene.BlToUnShader_uvtex+".y,1.0, 1.0);"
def define_UVMAP(name):
    return [defineVarible(name,1),"",""]


def VALTORGB(name, value, color_ramp):
    
    output = ""
    
    #taken from map range
    #result = "("+to_min+".r + (("+value+".r - "+from_min+".r)/("+from_max+".r - "+from_min+".r)) * ("+to_max+".r - "+to_min+".r))"
    
    if(color_ramp.interpolation == "LINEAR"):
        
        
        #This is what I was trying to do hope it worked:
        
        #1. map the ranges between each element in the gradient from 0-1
        #2. lerp between the colors of each element in the gradent using the mapped ranges
        #3. lerp between lerps with the mapped ranges of the input using the begginging of the first lerp and the end of the second lerp.
        
        #THIS IS BROKEN!!!
        #at least it's a good start.......
        
        arr = []
        
        for point in color_ramp.elements:
            arr.append(point)
        
        
        bubbleSortRamp(arr)
        
        
        pointpairs = list(chunks(arr,2))
        
        
        pointpairs2 = []
        
        #need to do first level
        for pair in pointpairs:
            if(len(pair) == 2):
                
                to_min = str(0)
                to_max = str(1)
                from_max = str(pair[1].position)
                from_min = str(pair[0].position)
                
                factor = "("+to_min+".r + (("+value+".r - "+from_min+".r)/("+from_max+".r - "+from_min+".r)) * ("+to_max+".r - "+to_min+".r))"
                
                color1 = "float4("+str(pair[0].color[0])+","+str(pair[0].color[1])+","+str(pair[0].color[2])+","+str(pair[0].color[3])+")"
                color2 = "float4("+str(pair[1].color[0])+","+str(pair[1].color[1])+","+str(pair[1].color[2])+","+str(pair[1].color[3])+")"
                
                pointpairs2.append(["lerp("+color1+","+color2+","+factor+")",[from_min,from_max]])
        
        pointpairs = list(chunks(pointpairs2,2))
        
        
        while(len(pointpairs) > 1):
            pointpairs2 = []
            
            for i,pair in enumerate(pointpairs):
                if(len(pair) > 1):
                    #refrence of what assembled pairs would look like
                    #[["lerp("+color1+","+color2+","+factor+")",[from_min,from_max]],["lerp("+color1+","+color2+","+factor+")",[from_min,from_max]]]
                    
                    to_min = str(0)
                    to_max = str(1)
                    from_max = str(pair[1].position)
                    from_min = str(pair[0].position)
                    
                    color1 = pair[0][0]
                    color2 = pair[1][0]
                    
                    
                    factor = "("+to_min+".r + (("+value+".r - "+from_min+".r)/("+from_max+".r - "+from_min+".r)) * ("+to_max+".r - "+to_min+".r))"
                    
                    pointpairs2.append(["lerp("+color1+","+color2+","+factor+")",[from_min,from_max]])
                else:
                    to_min = str(0)
                    to_max = str(1)
                    from_min = str(pointpairs2[len(pointpairs2)-1][1][0])
                    from_max = str(pair[0][1][1])
                    
                    
                    
                    
                    
                    color1 = pointpairs2[len(pointpairs2)-1][0]
                    color2 = pair[0][0]
                    
                    factor = "("+to_min+".r + (("+value+".r - "+from_min+".r)/("+from_max+".r - "+from_min+".r)) * ("+to_max+".r - "+to_min+".r))"
                    
                    pointpairs2.append(["lerp("+color1+","+color2+","+factor+")",[from_min,from_max]])
            
            pointpairs = pointpairs2.copy()
            
        #output = name+"[0] = "+float4ify(str(pointpairs[0]))+";"
        output = name+"[0] = "+float4ify("1.0")+";"
    
    return "//\"Node \'"+name+"\' type: \'VALTORGB\' Is not fully implemented. Here is a crappy placeholder for now."+"\n            "+output
def define_VALTORGB(name):
    return [defineVarible(name,1),"",""]


def VALUE(name):
    return ""
def define_VALUE(name,defaultvalue):
    return [defineVarible(name,1)+"\n            "+name+"[0] = "+float4ify("_"+name+"_input")+";", "float _"+name+"_input;","_"+name+"_input(\"Input Value \'"+name+"\'\", Float) = "+str(defaultvalue)]


def CURVE_VEC(name, factor, vector):
    return "//\"Node \'"+name+"\' type: \'CURVE_VEC\' is yet to be implemented! Here is a placeholder. I need someone who can figure this one out. - @989onan "+"\n            "+name+"[0] = "+float4ify("1.0")+";"
def define_CURVE_VEC(name):
    return [defineVarible(name,1),"",""]


#screw it. We are now using array input for this one because that's easier.
def VECT_MATH(name, array, mode):
    #26 cases
    array2 = []
    for vector in array:
        array2.append(vector.strip("\""))
    array = array2.copy()
    
    if(mode == "ADD"):
        return name+"[0] = "+"("+array[0]+" + "+array[1]+");"
    elif(mode == "SUBTRACT"):
        return name+"[0] = "+"("+array[0]+"  - "+array[1]+");"
    elif(mode == "MULTIPLY"):
        return name+"[0] = "+"("+array[0]+"  * "+array[1]+");"
    elif(mode == "DIVIDE"):
        return name+"[0] = "+"("+array[0]+"  / "+array[1]+");"
    elif(mode == "CROSS_PRODUCT"):
        return name+"[0] = "+"cross("+array[0]+" ,"+array[1]+");"
    elif(mode == "PROJECT"):
        length = "dot("+array[0]+" ,"+array[1]+")"
        return name+"[0] = (dot("+array[0]+" , "+array[1]+" ) / ("+length+" * "+length+"))/"+array[1]+" ;"
    elif(mode == "REFLECT"):
        return name+"[0] = reflect("+array[0]+" ,normalize("+array[1]+" ));"
    elif(mode == "REFRACT"):
        return name+"[0] = refract("+array[0]+" ,normalize("+array[0]+" ),"+array[0]+".r);"
    elif(mode == "FACEFORWARD"):
        return name+"[0] = "+float4ify("1.0")+"; //How to do? - @989onan"
    elif(mode == "DOT_PRODUCT"):
        return name+"[0] = "+float4ify("dot("+array[0]+" , "+array[1]+" )")+";"
    elif(mode == "DISTANCE"):
        return name+"[0] = "+float4ify("distance("+array[0]+" , "+array[1]+" )")+";"
    elif(mode == "LENGTH"):
        return name+"[0] = "+float4ify("length("+array[0]+" )")+";"
    elif(mode == "SCALE"):
        return name+"[0] = ("+array[0]+"  * "+array[1]+");"
    elif(mode == "NORMALIZE"):
        return name+"[0] = normalize("+array[0]+");"
    elif(mode == "ABSOLUTE"):
        return name+"[0] = =abs("+array[0]+");"
    elif(mode == "MINIMUM"):
        return name+"[0] = min("+array[0]+" , "+array[1]+" );"
    elif(mode == "MAXIMUM"):
        return name+"[0] = max("+array[0]+" , "+array[1]+" );"
    elif(mode == "FLOOR"):
        return name+"[0] = floor("+array[0]+" );"
    elif(mode == "CEIL"):
        return name+"[0] = ceil("+array[0]+" );"
    elif(mode == "FRACTION"):
        return name+"[0] = "+array[0]+" - floor("+array[0]+" );"
    elif(mode == "MODULO"):
        return name+"[0] = fmod("+array[0]+" , "+array[1]+" );"
    elif(mode == "WRAP"):
        return name+"[0] = "+float4ify("1.0")+"; //How to do? - @989onan"
    elif(mode == "SNAP"):
        return name+"[0] = "+float4ify("1.0")+"; //How to do? - @989onan"
    elif(mode == "SINE"):
        return name+"[0] = sin("+array[0]+" ;"
    elif(mode == "COSINE"):
        return name+"[0] = cos("+array[0]+" ;"
    elif(mode == "TANGENT"):
        return name+"[0] = tan("+array[0]+" ;"
            
def define_VECT_MATH(name):
    return [defineVarible(name,1),"",""]


#invert is true or false. Any mode that doesn't show an inout will be set to float4(1.0,1.0,1.0,1.0)
#need to incoportate invert into outputted code!!!
def VECTOR_ROTATE(name, vector, center, axis, angle, rotation, mode, invert):
    
    output = ""
    
    if(mode == "AXIS_ANGLE"):
        vector = vector+"-"+center
        output += "float mat_"+name+"[3][3];"
        
        output += "\n            "+"axis_angle_to_mat3(mat_"+name+","+axis+","+angle+")"
        output += "\n            "+name+"[0] = (mat_"+name+" * "+vector+");"
    elif(mode == "X"):#placeholders
        output += name+"[0] = "+float4ify("1.0")+";//anything refrencing this is broken!"
    elif(mode == "Y"):
        output += name+"[0] = "+float4ify("1.0")+";//anything refrencing this is broken!"
    elif(mode == "Z"):
        output += name+"[0] = "+float4ify("1.0")+";//anything refrencing this is broken!"
    elif(mode == "EULER_XYZ"):
        output += name+"[0] = "+float4ify("1.0")+";//anything refrencing this is broken!"
    
    
    return output
def define_VECTOR_ROTATE(name):
    return [defineVarible(name,1),"",""]


def VECT_TRANSFORM(name, vector, convert_from, convert_to):
    if(convert_from == convert_to):
        return name+"[0] = "+vector+";"
    else:
        if(convert_to == "WORLD"):
            if(convert_from == "OBJECT"):
                return name+"[0] = "+"mul(unity_ObjectToWorld,"+vector+");"
            elif(convert_from == "CAMERA"):
                return name+"[0] = "+"mul(unity_ObjectToCamera, "+vector+");"
        elif(convert_to == "OBJECT"):
            if(convert_from == "CAMERA"):
                return name+"[0] = "+"mul(unity_CameraToObject, "+vector+");"
            elif(convert_from == "WORLD"):
                return name+"[0] = "+"mul(unity_WorldToObject,"+vector+");"
        elif(convert_to == "CAMERA"): 
            if(convert_from == "OBJECT"):
                return name+"[0] = "+"mul(unity_ObjectToCamera, "+vector+");"
            elif(convert_from == "WORLD"):
                return name+"[0] = "+"mul(unity_WorldToCamera, "+vector+");"
    return "//New type for \""+name+"\" node not implemented yet! file a bug report with details!"
def define_VECT_TRANSFORM(name):
    return [defineVarible(name,1),"",""]


def VERTEX_COLOR(name):
    return name+"[0] = float4(IN.vertexColor.r,IN.vertexColor.g,IN.vertexColor.b,IN.vertexColor.a);"+"\n            "+name+"[1] = "+float4ify("IN.vertexColor.a")+";"
def define_VERTEX_COLOR(name):
    return [defineVarible(name,2),"",""]


#pixelsize is true or false.
#Someone implement this into our surface shader!
def WIREFRAME(name, size, pixelsize):
    return "//\"Node \'"+name+"\' type: \'WIREFRAME\' is yet to be implemented! Here is a placeholder. I need someone who can figure this one out. - @989onan "+"\n            "+name+"[0] = "+float4ify("0.0")+";"
def define_WIREFRAME(name):
    return [defineVarible(name,1),"",""]




##END NODE CLASS TYPES
##END NODE CLASS TYPES
##END NODE CLASS TYPES


def nodeError(inputchild,outputparent,LSide,RSide):
    return "//Unhandled "+outputparent.type+" going into "+inputchild.type+" Details: \n            LSide = \""+LSide+"\" RSide = \""+RSide+"\""+"//Error Info: input type was \""+inputchild.type+"\" output type was \""+outputparent.type+"\" node type for input was: \""+getNodeType(inputchild)+"\" Node type for output was \""+getNodeType(outputparent)+"\" Socket input node Name \""+inputchild.node.label+"\" Socket output node name was:\""+outputparent.node.label+"\""
def getNodeType(NodeSocket):
    return NodeSocket.node.type+""



#used in VALTORGB to assemble generated pairs for interpolation.
#CREDIT: https://stackoverflow.com/a/312464
#thank the internet ^_^ - @989onan
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#used in VALTORGB to assemble generated pairs for interpolation.
#CREDIT: https://www.geeksforgeeks.org/python-program-for-bubble-sort/
#thank the internet ^_^ - @989onan
def bubbleSortRamp(arr):
    n = len(arr)
  
    # Traverse through all array elements
    for i in range(n-1):
    # range(n) also work but outer loop will repeat one time more than needed.
  
        # Last i elements are already in place
        for j in range(0, n-i-1):
  
            # traverse the array from 0 to n-i-1
            # Swap if the element found is further along the gradient
            # than the next element
            if arr[j].position > arr[j + 1].position :
                arr[j], arr[j + 1] = arr[j + 1], arr[j]


#this uses Kahn's algorithm. Sudo code taken from: https://en.wikipedia.org/wiki/Topological_sorting
def sortNodes(materialoriginal):
    
    material = materialoriginal.copy() #copy material so we can do destructive actions without messing up original (like what is done in the sorting algorithm)
    L = []#← Empty list that will contain the sorted elements
    S = []#← Set of all nodes with no incoming edge
    nodetree = material.node_tree
    while(len(nodetree.nodes) > 0): 
        
        
        S = []
        
        #regrab nodes that have no inputs
        for node in nodetree.nodes:
            isNodeInputted = False
            for input in node.inputs:
                if(input.is_linked):
                    isNodeInputted = True
            if(not isNodeInputted):
                S.append(node)
                    
        #sort through all current nodes that don't have inputs, including their children for removing connections according
        #to the sorting algorithm.
        for node in S:
            children = []
            
            #Add the node to the sorted list if it hasn't been added yet (This is important! It prevents doubling up on every node in the tree that isn't an end or beginning node!)
            if(not node.name == ""):
                L.append(materialoriginal.node_tree.nodes[node.name]) if materialoriginal.node_tree.nodes[node.name] not in L else L #append the equivalent node to the sorted list of the original material's nodes
            else:
                nodetree.nodes.remove(node)
                continue
            #find all nodes that connect to current node (so children)
            for output in node.outputs:
                for child in output.links:
                    children.append(child.to_node)
            
            #iterate through children nodes. If we remove their connections to the current node and they don't have connections left, add them to sorted. 
            childrenHaveConnections = False
            for child in children:
                for nodesocket in child.inputs:
                    for link in nodesocket.links:
                        if(link.from_node == node):
                            nodetree.links.remove(link)
                for nodesocket in child.inputs:
                    if(len(nodesocket.links) > 0):
                        childrenHaveConnections = True
                if not childrenHaveConnections:
                    L.append(materialoriginal.node_tree.nodes[child.name]) #append the equivalent node to the sorted list of the original material's nodes         
            
            #remove the current node since it is now an island 
            nodetree.nodes.remove(node)
                
    
    bpy.data.materials.remove(material)#delete our material copy to not leave junk for the user to clean up.
    
    return L



#CREDIT: https://blender.stackexchange.com/a/110112 

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


##INTERFACE STUFF - by @989onan

class VIEW3D_PT_BlenderToUnityPanel(bpy.types.Panel):
    """Main Blender To Unity Panel"""
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderToUnity'
    bl_context = 'objectmode'
    bl_label = "Shader Blender To Unity" 
    
    def draw(self,context):
        
        scene = context.scene
        row = self.layout.row()
        if(context.active_object is not None):
            row.operator('object.blendertounityshaderall',text = "Convert Blender to Unity Shaders", icon = "MATERIAL")
        else:
            row.label(text = "-No active object-")
        if(context.active_object is not None):
            row.operator('object.blendertounityshaderone',text = "Convert One Material to Unity Shaders", icon = "MATERIAL")
        else:
            row.label(text = "-No active object-")
        row.prop(bpy.context.scene, "BlToUnShader_debugmode", text="Enable/Disable Debug Mode")
        

def start(context, all):
    scene = context.scene
    
    rawMaterials = readNodeTrees(all)
    
    for material in rawMaterials:
        GeneratedFile = writeNodeData(material[0],material[1],material[2],material[3])
        writedebug("\n======================="+material[0].name+"=======================")
        writedebug("\n"+GeneratedFile)
        writedebug("\nWriting this data to: "+bpy.path.abspath("//")+""+material[0].name+".shader")
        
        if(bpy.data.is_saved):
            
            file = open(bpy.path.abspath("//")+material[0].name+".shader", "w")
            
            GeneratedFile = GeneratedFile.replace(".jpg", "")
            GeneratedFile = GeneratedFile.replace(".png", "")
            
            file.write(GeneratedFile)
            file.close()
            if(scene.BlToUnShader_debugmode == True):
                
                writedebug("\nWriting Debug Text File to: "+bpy.path.abspath("//")+""+material[0].name+"_debug.txt")
                file = open(bpy.path.abspath("//")+material[0].name+"_debug.txt", "w")
                file.write(scene.BlToUnShader_debugfile)
                file.close()
        else:
            ShowMessageBox("Error! Please save this blender file somewhere before trying to generate a shader!", "Blender Nodes To Unity Shader", 'ERROR')
    
    



class OBJECT_OT_MakeShader(bpy.types.Operator):
    """Convert Blender Material to Unity Shader"""
    
    bl_idname = "object.blendertounityshaderall"
    bl_label = "Convert Blender to Unity Shaders"
    bl_options = {'REGISTER'}
    
    
    
    def execute(self,context):
        start(context, True)
        return {'FINISHED'}

class OBJECT_OT_MakeOneShader(bpy.types.Operator):
    """Convert Blender Material to Unity Shader"""
    
    bl_idname = "object.blendertounityshaderone"
    bl_label = "Convert Blender to Unity Shaders"
    bl_options = {'REGISTER'}
    
    
    
    def execute(self,context):
        start(context, False)
        return {'FINISHED'}


def register():
    bpy.types.Scene.BlToUnShader_debugmode = bpy.props.BoolProperty(name="Debug Mode",description="Enable/Disable Debug Mode",default = False)
    bpy.types.Scene.BlToUnShader_uvtex = bpy.props.StringProperty(name="uvtex", default="")
    bpy.types.Scene.BlToUnShader_debugfile = bpy.props.StringProperty(name="debugfile", default="")
    bpy.utils.register_class(OBJECT_OT_MakeShader)
    bpy.utils.register_class(OBJECT_OT_MakeOneShader)
    bpy.utils.register_class(VIEW3D_PT_BlenderToUnityPanel)
    

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_MakeShader)
    bpy.utils.unregister_class(VIEW3D_PT_BlenderToUnityPanel)
    bpy.utils.unregister_class(OBJECT_OT_MakeOneShader)
    del bpy.types.Scene.BlToUnShader_debugmode
    del bpy.types.Scene.BlToUnShader_uvtex
    del bpy.types.Scene.BlToUnShader_debugfile

if __name__ == "__main__":
    register()