import cherrypy

from tempfile import gettempdir






class HelloWorld:
    def index(self):

      raise Exception('Nerf')
      pass
    index.exposed = True

if __name__ == '__main__':
    pass
  
class HelloWorld2:
    def index(self):
        #return "Hello world2!"
        #mylookup = TemplateLookup(directories=['templates'],module_directory=gettempdir()+'/mako_modules', collection_size=200,output_encoding='utf-8', encoding_errors='replace')
        #mytemplate = Template("""<%include file="foo.txt"/>, hello world!""", lookup=mylookup)
        
      pass
#        return mytemplate.render(name="jack")

    index.exposed = True
    
    def serve_template(self,templatename, **kwargs):
      #mytemplate = mylookup.get_template(templatename)
      #print mytemplate.render(**kwargs)
      pass


