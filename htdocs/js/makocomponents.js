$.fn.scrollView = function() {
    return this.each(function() {
        $('html, body').animate({
            scrollTop : $(this).offset().top
        }, 1000);
    });
}

function getResponseConent(response) {
    if ((response.status == 403) || (response.status == 404)) {
        var message = getErrorMsg(response)
        return message
    } else {
        
        var message = response.responseText
        document.write(message); 
        return message;
    }
}

function getResonseTextContent(responseText) {
    if (responseText.match(/(<html)/i)) {
        document.write(responseText); 
        return responseText;
    } else {
        if (responseText.match(/^<!--Error-->/gi)) {
            return createErrorsMsg(null, responseText);
        }
        return responseText;
    }
}

function createErrorsMsg(code, message) {
    var resultText = '<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
    if (code != null) {
        resultText += '<h4 class="alert-heading" style="text-align:left">Error: ' + code
                + '</h4><p><div style="text-align:left">'
    } else {
        resultText += '<h4 class="alert-heading" style="text-align:left">Error occurred!</h4><p><div style="text-align:left">'
    }
    resultText += message;
    resultText += '</div></p></div>';
    return resultText
}

function getErrorMsg(resonseText) {

    if (typeof (resonseText.statusText) !== 'undefined') {
        var message = resonseText.statusText;
    } else {
        var message = resonseText;
    }
    if (typeof (resonseText.status) !== 'undefined') {
        var code = resonseText.status
    } else {
        var code = null
    }
    return createErrorsMsg(resonseText.status,message);
}

function formEvent(element, event, uri, contentid, doRefresh, refreshContainer,
        refreshUrl) {

    genericFormSubmit(element, event, null, contentid, uri, doRefresh,
            refreshContainer, refreshUrl);
}

function formSubmit(formElement, event, modalID, uri, doRefresh,
        refreshContainer, refreshUrl) {
    genericFormSubmit(formElement, event, modalID, null, uri, doRefresh,
            refreshContainer, refreshUrl);
}

function genericFormSubmit(formElement, event, modalID, contentid, uri,
        doRefresh, refreshContainer, refreshUrl) {
    var form = $(formElement);
    var inputs = form.find("input, select, button, textarea");
    var formData = new FormData(form[0]);

    //disable the inputs
    inputs.prop("disabled", true);

    var request = $.ajax({
        url : uri,
        type : "post",
        data : formData,
        contentType: false,
        processData: false,
     timeout: 30000 //3secs
    });

    request.error(function(response, textStatus, XMLHttpRequest) {
        var message = getResponseConent(response);
        if (modalID) {
            $('#' + modalID + 'body').html(resultText);
        } else {

            $('#' + contentid + 'Errors').html(resultText);
        }
    });
    
    request.success(function(responseText, textStatus, XMLHttpRequest) {
        var message = getResonseTextContent(responseText);
        if (responseText.match(/^<!--OK--/gi)) {
            if (modalID) {
                $("#" + modalID).modal('hide');
            }
            // refrehshPage & container if needed
            if (doRefresh) {
                form[0].reset();
                if (refreshUrl != "None") {
                    loadContent(refreshContainer, refreshUrl);
                } else {
                    $("#" + refreshContainer).html(responseText);
                }

            }
        } else {
            if (responseText.match(/^<!--Error-->/gi)) {
                var resultText = createErrorsMsg(null, responseText);
                form.prepend(resultText);
                
            } else {
                if (responseText.match(/^<!--PostError-->/gi)) {
                    var resultText = createErrorsMsg(null, responseText);
                } else {
                    var resultText = responseText;
                } 
                if (modalID) {
                    $("#" + modalID + "body").html(resultText);
                } else {
                    $("#" + refreshContainer + "").html(resultText);
                }
            }
        }
    });

    request.always(function() {
        // reenable the inputs
        inputs.prop("disabled", false);
    });
    // prevent default posting of form
    event.preventDefault();

}

function loadContent(contentid, url) {
    //Append new div to content
    if (contentid.match(/Hidden$/)) {
        var hiddenDiv = contentid;
    } else {
        var hiddenDiv = getHiddenDivID(contentid, contentid);
    }
    if ((hiddenDiv) && (url)) {
        $("#" + hiddenDiv).html(
                '<img src="/img/ajax-loader.gif" alt="loading"/> ');
        // load Content
        var request = $.ajax({
            url : url,
         timeout: 30000 //3secs
        });
        
        request.error(function(response, textStatus, XMLHttpRequest) {
            var message = getResponseConent(response);
            $("#" + hiddenDiv).html(message);
        });
        request.success(function(responseText, textStatus, XMLHttpRequest) {
            var message = getResonseTextContent(responseText);
            $("#" + hiddenDiv).html(message);
        });
    }
}

function loadNewTab(pk, id, url, reload, title) {
    // getTabID
    var tabID = id.replace("TabContent", "");
    // deactivate Tabs
    // deactivateActiveOne
    $('#' + tabID).find("li").each(function() {
        $(this).attr('class', 'dropdown');
    });
    // check if element exists
    if ($('#' + tabID + pk + 'LI').length) {
        $('#' + tabID + pk + 'LI').attr('class', 'dropdown active');
    } else {
        // createTab
        var keyValue = tabID+pk
        var tab = $("<li/>")
        .attr("id", keyValue +'LI')
        .attr("class", 'dropdown active');
        var link = $('<a/>')
        .attr("href", '#')
        .attr("class", 'dropdown-toggle active')
        .attr("data-toggle", 'dropdown')
        .attr("src", url)
        .attr("onclick", '#')
        .attr("id", keyValue)
        .html(title+'<span class="caret"></span>');
        if (reload) {
            link.attr("onclick", 'loadTabLi(this.id, true)');
        } else {
              link.attr("onclick", 'loadTabLi(this.id, false)');
        }
        var dropdown = $('<ul/>')
            .attr("class", 'dropdown-menu')
            .attr("role", 'menu');
        if (!reload) {
            var menuItem = $('<li/>')
            var reload =  $('<a/>')
            .attr("href", '#')
            .attr("tabindex", '-1')
            .attr("onclick", "loadTabLi('"+keyValue+"', true);")
            .html('Reload');
            menuItem.append(reload);
            dropdown.append(menuItem);
        }
        var menuItem2 = $('<li/>')
        var close = $('<a/>')
        .attr("href", '#')
        .attr("tabindex", '-1')
        .attr("onclick", 'closeTab(\'' + tabID + '\',\'' + tabID + pk + 'LI\');')
        .html('Close');
        menuItem2.append(close);
        dropdown.append(menuItem2);

        tab.append(link);
        tab.append(dropdown);
        
        $("#" + tabID).append(tab);
    }
    // load Content
    loadContent(id, url);
}

function closeTab(tabulatorID, tabToCloseID) {

    $('#' + tabToCloseID).find("a").each(function() {
        // normalerweis get et just een
        $(this).attr('onclick', '').unbind('click');
    });

    $('#' + tabToCloseID).remove();
    //empty contents of pane
    var conentID = tabulatorID+"TabContent";
    var hiddenDiv = getHiddenDivID(conentID, conentID);
    $('#'+hiddenDiv).html("");
    // goback to first tab
    $('#' + tabulatorID).find('li').each(function() {
        // loadfirst tab
        var firstID = this.id;
        //RemovesLI
        var identifier = firstID.substr(0,firstID.length-2);
        activateLi(identifier);
        $(this).find('a').each(function(){
            var url = $(this).attr('src');
            return loadTab(url, identifier)
        });
        
        return false;
    });
}

function activateLi(id) {
    // deactivateActiveOne
    $('#' + id + 'LI').parent().find("li").each(function() {
        $(this).attr('class', 'dropdown');
    });
    // activate tab
    $('#' + id + 'LI').attr('class', 'dropdown active');
}

function loadTab(url, id) {
    activateLi(id);
    var parentName = $('#' + id + 'LI').parent().attr('id');
    loadContent(parentName + 'TabContent', url);
}

function findAndLoadActiveLi(id, contentID) {
    $('#' + id).find("li").each(function() {
        var item = $(this);
        var className = item.attr('class');
        if (className) {
            if (className.match(/active/i)) {
                item.find("a").each(function() {
                    url = $(this).attr('src');
                    return loadContent(contentID, url);
                });
            }
        }
    })
}

function hideHidden(contentID) {
    $('#' + contentID).children('div').each(function() {
        if (this.id.match(/Hidden$/)) {
            return $(this).css("display", "none");
        }
    });
}

function getHiddenDivID(id, contentID) {
    var found = false;
    //hide all in container
    hideHidden(contentID);
    var hiddenID =   id + 'Hidden';
    var parentDiv = $('#' + contentID);
    var parentParend = parentDiv.parent();
    //heck if one is existing and then show it else
    parentDiv.children('div').each(function() {
        if (this.id == hiddenID) {
            $(this).css("display", "block");
            found = true;
        }
    });
    //if noone found append a new one
    
    if (!found) {
        var $div = $("<div/>")
        .attr("id", hiddenID)
        .html("");

        parentDiv.append($div);
    }
    
    return hiddenID;
    
    
}

function loadToolbarLi(id, contentID, reload) {

    activateLi(id);
    var url = $('#' + id).attr('src');
    hideHidden(contentID + 'Hidden');
    if (reload) {
        loadContent(contentID, url);
    } else {
        var hiddenDivID = getHiddenDivID(id, contentID);
        //if div is empty load content 
        if ($('#' + hiddenDivID).is(':empty')) {
            loadContent(hiddenDivID, url);
        } else {
            //show content
            $('#' + hiddenDivID).css("display", "block");
        }
    }
}

function loadTabLi(id, reload) {
    var obj = $("#" + id + "LI");
    var ul = obj.closest('ul');
    var parentName = ul.get(0).id;
    parentName = parentName.replace(/\uFFFD/g, '');
    loadToolbarLi(id, parentName + "TabContent", reload);
}


function genericDialogCall(url, refreshContainer, refreshUrl, refreshContent,
        doCloseTab, tabID, tabToClose) {

    
    var request = $.ajax({
        url : url,
     timeout: 30000 //3secs
    });
    request.error(function(response, textStatus, XMLHttpRequest) {
        var message = getResponseConent(response);
        alert(message);
    });
    request.success(function(responseText, textStatus, XMLHttpRequest) {
        var message = getResonseTextContent(responseText);
        if (message.match(/^<!--OK--/gi)) {
            // do refresh
            if (refreshContent) {
                loadContent(refreshContainer, refreshUrl);
            } else {
                if (doCloseTab) {
                    closeTab(tabID, tabToClose);
                }
            }
        } else {
            if (message.match(/^<!--Error-->/gi)) {
                var startPos = message.lastIndexOf('>');
                message = message.substring(startPos+1);
            }
            alert('Error:\n' + message);
        }
    });

}

function dialogCall(url, refreshContainer, refreshUrl) {
    genericDialogCall(url, refreshContainer, refreshUrl, true, false, '', '');
}

function dialogCloseTabCall(url, tabID, tabToClose) {
    genericDialogCall(url, '', '', false, true, tabID, tabToClose);
}

function activateMenuLi(id) {
    // deactivateActiveOne
    $('#' + id).parent().parent().find("li").each(function() {
        $(this).attr('class', '');
    });
    // activate tab
    $('#' + id).parent().attr('class', 'active');
}

function resizeScrollPannel(id) {
    var div = $(id);
    var windowHeight = $(window).height() - 300;
    div.css({'height': windowHeight+'px' });
}