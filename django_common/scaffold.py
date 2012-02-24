from os import path, remove, system, listdir, sys

# VIEW CONSTS

LIST_VIEW = """
def %(lower_model)s_list(request, template='%(lower_model)s/list.html'):
    d = {}
    d['%(lower_model)s_list'] = %(model)s.objects.all()
    return render(request, template, d)
"""

DETAILS_VIEW = """
def %(lower_model)s_details(request, id, template='%(lower_model)s/details.html'):
    d = {}
    d['%(lower_model)s'] = %(model)s.objects.get(pk=id)
    return render(request, template, d)
"""

DELETE_VIEW = """
def %(lower_model)s_delete(request, id):
    item = %(model)s.objects.get(pk=id)
    item.delete()
    return redirect(reverse('%(lower_model)s_list'))
"""
# MODELS CONSTS

SCAFFOLD_APPS_DIR = 'apps'

MODEL_TEMPLATE = """
class %s(models.Model):
    %s
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-id']
"""

IMPORT_MODEL_TEMPLATE = """from %(app)s.models import %(model)s"""

CHARFIELD_TEMPLATE = """
    %(name)s = models.CharField(max_length=%(length)s, null=%(null)s, blank=%(null)s)
"""

TEXTFIELD_TEMPLATE = """
    %(name)s = models.TextField(null=%(null)s, blank=%(null)s)
"""

INTEGERFIELD_TEMPLATE = """
    %(name)s = models.IntegerField(null=%(null)s, default=%(default)s)
"""

DECIMALFIELD_TEMPLATE = """
    %(name)s = models.DecimalField(max_digits=%(digits)s, decimal_places=%(places)s, null=%(null)s, default=%(default)s)
"""

DATETIMEFIELD_TEMPLATE = """
    %(name)s = models.DateTimeField(null=%(null)s, default=%(default)s)
"""

FOREIGNFIELD_TEMPLATE = """
    %(name)s = models.ForeignKey(%(foreign)s)
"""

class Scaffold(object):

    def _info(self, msg, indent=0):
        print "%s %s" % ("\t"*int(indent), msg)

    def __init__(self, app, model, fields):
        self.app = app
        self.model = model
        self.fields = fields
    
    def get_import(self, model):
        for dir in listdir(SCAFFOLD_APPS_DIR):
            if path.isdir('%s/%s' % (SCAFFOLD_APPS_DIR,dir)) and path.exists('%s/%s/models.py' % (SCAFFOLD_APPS_DIR,dir)):
                dir_models_file = open('%s/%s/models.py' % (SCAFFOLD_APPS_DIR,dir), 'r')
                # Check if model exists
                for line in dir_models_file.readlines():
                    if 'class %s(models.Model)' % model in line:
                        #print "Foreign key '%s' was found in app %s..." % (model, dir)
                        return IMPORT_MODEL_TEMPLATE % {'app': dir, 'model': model }
        return None
        
    def is_imported(self, path, model):
        import_file = open(path, 'r')
        for line in import_file.readlines():
            if 'import %s' % model in line:
                #print "Foreign key '%s' was found in models.py..." % (foreign)
                return True
        return False
        
    def add_global_view_imports(self, path):
        #from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
        import_list = list()
        import_file = open(path, 'r')
        
        need_import_shortcut = True
        need_import_urlresolvers = True
        
        for line in import_file.readlines():
            if 'from django.shortcuts import render, redirect, get_object_or_404' in line:
                need_import_shortcut = False
            if 'from django.core.urlresolvers import reverse' in line:
                need_import_urlresolvers = False
        
        if need_import_shortcut:
            import_list.append('from django.shortcuts import render, redirect, get_object_or_404')
        if need_import_urlresolvers:
            import_list.append('from django.core.urlresolvers import reverse')
            
        return import_list
        
    def view_exists(self, path, view):
        # Check if view already exists
        view_file = open(path, 'r')
        for line in view_file.readlines():
            if 'def %s(' % view in line:
                return True
        return False
        
    def get_field(self, field):
        field = field.split(':')
        field_type = field[0]
        if field_type.lower() == 'char':
            try:
                length = field[2]
            except:
                length = 255
            try:
                null = field[3]
                null = 'False'
            except:
                null = 'True'                
            return CHARFIELD_TEMPLATE % {'name': field[1], 'length': length, 'null': null}
        elif field_type.lower() == 'text':
            try:
                null = field[2]
                null = 'False'
            except:
                null = 'True'                
            return TEXTFIELD_TEMPLATE % {'name': field[1], 'null': null}
        elif field_type.lower() == 'int':
            try:
                null = field[2]
                null = 'False'
            except:
                null = 'True'
            try:
                default = field[3]
            except:
                default = None  
            return INTEGERFIELD_TEMPLATE % {'name': field[1], 'null': null, 'default': default}
        elif field_type.lower() == 'decimal':
            try:
                null = field[4]
                null = 'False'
            except:
                null = 'True'
            try:
                default = field[5]
            except:
                default = None  
            return DECIMALFIELD_TEMPLATE % {'name': field[1], 'digits': field[2], 'places':field[3], 'null': null, 'default': default}
        elif field_type.lower() == 'datetime':
            try:
                null = field[2]
                null = 'False'
            except:
                null = 'True'
            try:
                default = field[3]
            except:
                default = None  
            return DATETIMEFIELD_TEMPLATE % {'name': field[1], 'null': null, 'default': default}
        elif field_type.lower() == 'foreign':
            foreign = field[1]
            name = foreign.lower()
            # Check if this foreign key is already in models.py
            if self.is_imported('%s/%s/models.py' % (SCAFFOLD_APPS_DIR, self.app), foreign):
                return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign}
            # Check imports
            if self.get_import(foreign):
                self.imports.append(self.get_import(foreign))
                return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign}
            
            self._info('error\t%s/%s/models.py\t%s class not found' % (SCAFFOLD_APPS_DIR, self.app, field[1]), 1)
            return None
    
    def create_app(self):
        self._info("    App    ")
        self._info("===========")
        if not path.exists('%s/%s' % (SCAFFOLD_APPS_DIR, self.app)):
            system('python manage.py startapp %s' % self.app)
            system('mv %s %s/%s' % (self.app, SCAFFOLD_APPS_DIR, self.app))
            self._info("create\t%s/%s" % (SCAFFOLD_APPS_DIR, self.app), 1)
        else:
            self._info("exists\t%s/%s" % (SCAFFOLD_APPS_DIR, self.app), 1)
    
    def create_views(self):
        self._info("   Views   ")
        self._info("===========")
        # Open models.py to read
        view_path = '%s/%s/views.py' % (SCAFFOLD_APPS_DIR, self.app)
        
        self._info("create\t%s" % (view_path), 1)
        
        import_list = list()
        view_list = list()
        
        # Add global imports
        import_list.append('\n'.join(imp for imp in self.add_global_view_imports(view_path)))
        
        # Add model imports
        if not self.is_imported(view_path, self.model):
            import_list.append(self.get_import(self.model))
        
        lower_model = self.model.lower()
        
        # Check if view already exists
        if not self.view_exists(view_path, "%s_view" % lower_model):
            view_list.append(LIST_VIEW % {'lower_model': lower_model, 'model': self.model})
            self._info("added \t%s\t%s_view" % (view_path,lower_model), 1)
        
        if not self.view_exists(view_path, "%s_details" % lower_model):
            view_list.append(DETAILS_VIEW % {'lower_model': lower_model, 'model': self.model})
            self._info("added \t%s\t%s_details" % (view_path,lower_model), 1)
        
        if not self.view_exists(view_path, "%s_model" % lower_model):
            view_list.append(DELETE_VIEW % {'lower_model': lower_model, 'model': self.model})
            self._info("added \t%s\t%s_delete" % (view_path,lower_model), 1)
            
        # Open views.py to append
        view_file = open(view_path, 'a')
        
        view_file.write('\n'.join(import_line for import_line in import_list))
        view_file.write(''.join(view for view in view_list))
        
    
    def create_model(self):
        self._info("   Model   ")
        self._info("===========")
        # Open models.py to read
        self.models_file = open('%s/%s/models.py' % (SCAFFOLD_APPS_DIR, self.app), 'r')
        
        # Check if model already exists
        for line in self.models_file.readlines():
            if 'class %s' % self.model in line:
                self._info('exists\t%s/%s/models.py' % (SCAFFOLD_APPS_DIR, self.app), 1)
                return
        
        self._info('create\t%s/%s/models.py' % (SCAFFOLD_APPS_DIR, self.app), 1)
        # Prepare fields
        self.imports = list()
        fields = list()
        for field in self.fields:
            new_field = self.get_field(field)
            if new_field:
                fields.append(new_field)
                self._info('added\t%s/%s/models.py\t%s field' % (SCAFFOLD_APPS_DIR, self.app, field.split(':')[1]), 1)
            
        # Open models.py to append
        models_file = open('%s/%s/models.py' % (SCAFFOLD_APPS_DIR, self.app), 'a')
        
        models_file.write(''.join(import_line for import_line in self.imports))
        models_file.write(MODEL_TEMPLATE % (self.model, ''.join(field for field in fields)))
        
            
    def run(self):
        if not self.app:
            sys.exit("No application name found...")
        if not self.model:
            sys.exit("No model name found...")
            
        self.create_app()
        self.create_model()
        self.create_views()