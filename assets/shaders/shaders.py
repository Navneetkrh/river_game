object_shader = {
    "vertex_shader" : '''
        
        #version 330 core
        layout(location = 0) in vec3 vertexPosition;
        layout(location = 1) in vec3 vertexColour;

        out vec3 fragmentColour;

        uniform mat4 modelMatrix;
        uniform mat4 camMatrix;

        void main() {
            fragmentColour = vertexColour;
            gl_Position = camMatrix * modelMatrix * vec4(vertexPosition, 1.0);
        }

        ''',

        "fragment_shader" : '''

        #version 330 core

        in vec3 fragmentColour;
        out vec4 outputColour;

        void main() {
            outputColour = vec4(fragmentColour, 1.0); // Set color
        }

        '''

}