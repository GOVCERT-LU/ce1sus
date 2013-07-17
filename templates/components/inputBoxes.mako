<%def name="labeledInput(label, name, value, enabled=True, validationMsg=None, placeholder=None)">
    <div class="row-fluid">
         <div class="span2">
            <div style="padding: 5px;">
                <div>
                    <label> ${label}</label>
                </div>
            </div>
         </div>
         <div class="span9">
            ${genericInput(name, value, enabled, validationMsg, placeholder)}
         </div>
    </div>
</%def>

<%def name="genericInput(name, value, enabled=True, validationMsg=None, placeholder=None)">
    <%
    if (enabled):
        enabledStr = ''
    else:
        enabledStr =  ' disabled ' 
    
    if (placeholder is None):
        placeHStr = ''
    else:
        placeHStr = ' placeholder="'+placeholder+'" '
        
    if hasattr(value,'error'):
        validationMsg = getattr(value,'error')
        
    %>
    
    
    
    <div class="row-fluid">
        <div class="span12">
        <input name="${name}" type="text" ${placeHStr} value="${value}" ${enabledStr}/>
        % if (not (validationMsg is None)) and enabled:
            ${genericError(validationMsg)}
        % endif
        </div>
    </div>
</%def>

<%def name="genericError(message)">
    <div class="alert alert-error">
        ${message}
    </div>
</%def>


<%def name="userForm(user,enabled)">
        
        % if user is None:
            ${labeledInput(label='Identifier',name='userID',value='',enabled=False)}
            ${labeledInput(label='Username',name='username',value='',enabled=enabled)}
            ${labeledInput(label='Password',name='password',value='',enabled=enabled)}
            ${labeledInput(label='Email',name='email',value='',enabled=enabled)}
            ${labeledInput(label='last logged in',name='last_login',value='',enabled=False)}
            
        % else:
            <input type="hidden" name="identifier" value="${user.identifier}">
            ${labeledInput(label='Identifier',name='userID',value=user.identifier,enabled=False)}
            ${labeledInput(label='Username',name='username',value=user.username,enabled=enabled)}
            ${labeledInput(label='Password',name='password',value=user.password,enabled=enabled)}
            ${labeledInput(label='Email',name='email',value=user.email,enabled=enabled)}
            ${labeledInput(label='Last logged in',name='last_login',value=user.last_login,enabled=False)}
        % endif

</%def>

<%def name="groupForm(group,enabled)">
        
        % if group is None:
            ${labeledInput(label='Identifier',name='groupID',value='',enabled=False)}
            ${labeledInput(label='Name',name='name',value='',enabled=enabled)}
            ${labeledInput(label='ShareTLP',name='shareTLP',value='',enabled=enabled)}
        % else:
            <input type="hidden" name="identifier" value="${group.identifier}">
            ${labeledInput(label='Identifier',name='groupID',value=group.identifier,enabled=False)}
            ${labeledInput(label='Name',name='name',value=group.name,enabled=enabled)}
            ${labeledInput(label='ShareTLP',name='shareTLP',value=group.shareTLP,enabled=enabled)}
        % endif

</%def>

