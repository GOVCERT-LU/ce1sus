$.fn.scrollView = function() {
    return this.each(function() {
        $('html, body').animate({
            scrollTop : $(this).offset().top
        }, 1000);
    });
};

function getResponseConent(response) {
    if ((response.status === 403) || (response.status === 404)) {
        var message = getErrorMsg(response);
        return message;
    } else {
        var message = response.responseText;
        return generateErrorFromBody(message);
    }
}

function generateErrorFromBody(message){
    var bodyStart = message.indexOf('<body') + 5;
    var bodyEnd = message.indexOf('</body>');
    message = message.substring(bodyStart,bodyEnd); 
    bodyStart = message.indexOf('>')+1;
    message = message.substring(bodyStart); 
    //Remove powered tag
    bodyEnd = message.indexOf('<div id="');
    message = message.substring(0,bodyEnd);
    message = createErrorsMsg('FOO', message);
    return message;
}

function getResonseTextContent(responseText) {
    if (responseText.match(/(<html)/i)) {
        //document.write(responseText);
        return generateErrorFromBody(responseText);;
    } else {
        if (responseText.match(/^<!--Error-->/gi)) {
            return createErrorsMsg(null, responseText);
        }
        return responseText;
    }
}

function createErrorsMsg(code, message) {
    var resultText = '<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
    if (code !== null) {
        if (code==='FOO') {
            '<div style="text-align:left">';
        } else {
            resultText += '<h4 class="alert-heading" style="text-align:left">Error: ' + code
                + '</h4><p><div style="text-align:left">';
        }
    } else {
      resultText += '<h4 class="alert-heading" style="text-align:left">Error occurred!</h4><p><div style="text-align:left">';
    }
    resultText += message;
    resultText += '</div></p></div>';
    return resultText;
}

function getErrorMsg(resonseText) {

    if (typeof (resonseText.statusText) !== 'undefined') {
        var message = resonseText.statusText;
    } else {
        var message = resonseText;
    }
    if (typeof (resonseText.status) !== 'undefined') {
        var code = resonseText.status;
    } else {
        var code = null;
    }
    return createErrorsMsg(resonseText.status,message);
}

function formEvent(element, event, uri, contentid, doRefresh, refreshContainer,
        refreshUrl, sidenav) {

    genericFormSubmit(element, event, null, contentid, uri, doRefresh,
            refreshContainer, refreshUrl, sidenav);
}

function formSubmit(formElement, event, modalID, uri, doRefresh,
        refreshContainer, refreshUrl) {
    genericFormSubmit(formElement, event, modalID, null, uri, doRefresh,
            refreshContainer, refreshUrl);
}

function genericFormSubmit(formElement, event, modalID, contentid, uri,
        doRefresh, refreshContainer, refreshUrl, sidenav) {
    if(typeof(sidenav)==='undefined') sidenav = false;
    var form = $(formElement);
    var inputs = form.find("input, select, button, textarea");
    var formData = new FormData(form[0]);
    //disable the inputs
    inputs.prop("disabled", true);
    var request = $.ajax({
        url : uri,
        type : "POST",
        data : formData,
        contentType: false,
        processData: false,
        timeout: 30000 //3secs
    });
    request.fail(function(response, textStatus, XMLHttpRequest) {
        var message = getResponseConent(response);
        if (modalID) {
            $('#' + modalID + 'body').html(message);
        } else {

            $('#' + contentid + 'Errors').html(message);
        }
    });
    request.error(request.fail);
    request.done(function(responseText, textStatus, XMLHttpRequest) {
        var message = getResonseTextContent(responseText);
        if (message.match(/^<!--OK--/gi)) {
            form[0].reset();
            if (modalID) {
                $("#" + modalID).modal('hide');
            }
            // refrehshPage & container if needed
            if (doRefresh) {
                if (refreshUrl !== "None") {
                    refreshContainer = getHiddenDivID(refreshContainer, contentid);
                    loadContent(refreshContainer, refreshUrl);
                    $('#'+refreshContainer).css("display", "block");
                    if (sidenav) {
                      loadSideNav(sidenav, true);
                    }
                } else {
                    $("#" + refreshContainer).html(message);
                }
            }
        } else {
            if (message.match(/^<!--Error-->/gi)) {
                var resultText = createErrorsMsg(null, message);
                form.prepend(resultText);
            } else {
                if (message.match(/^<!--PostError-->/gi)) {
                    //post errors are mainly validations issues
                    var resultText = message;
                } else {
                    var resultText = createErrorsMsg(null, message);
                }
                if (modalID && !contentid) {
                    $("#" + modalID + "body").html(message);
                } else {
                    $("#" + contentid).html(message);
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

function genericDialogCall(url, refreshContainer, refreshUrl, refreshContent,
        doCloseTab, tabID, tabToClose) {
    var request = $.ajax({
        url : url,
     timeout: 30000 //3secs
    });
    request.fail(function(response, textStatus, XMLHttpRequest) {
        var message = getResponseConent(response);
        alert(message);
    });
    request.error(request.fail);
    request.done(function(responseText, textStatus, XMLHttpRequest) {
        var message = getResonseTextContent(responseText);
        if (message.match(/^<!--OK--/gi)) {
            // do refresh
            if (refreshContent) {
                refreshContainer = getHiddenDivID(refreshContainer, null);
                loadContent(refreshContainer, refreshUrl);
            }
            if (doCloseTab) {
                closeTab(tabID, tabToClose);
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
    genericDialogCall(url, 'recentEventsHidden', '/events/recent', true, true, tabID, tabToClose);
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
        request.fail(function(response, textStatus, XMLHttpRequest) {
            var message = getResponseConent(response);
            $("#" + hiddenDiv).html(message);
        });
        request.error(request.fail);
        request.done(function(responseText, textStatus, XMLHttpRequest) {
            var message = getResonseTextContent(responseText);
            $("#" + hiddenDiv).html(message);
        });
    }
}

function loadNewTab(pk, id, url, reload, title) {
    alert('deprecated');
    return false;
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
        var keyValue = tabID+pk;
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
            var menuItem = $('<li/>');
            var reloadLink =  $('<a/>')
            .attr("href", '#')
            .attr("tabindex", '-1')
            .attr("onclick", "loadTabLi('"+keyValue+"', true);")
            .html('Reload');
            menuItem.append(reloadLink);
            dropdown.append(menuItem);
        }
        var menuItem2 = $('<li/>');
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
    alert('deprecated');
    return false;
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
            return loadTab(url, identifier);
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
    alert('deprecated');
    return false;
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
    });
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
    //heck if one is existing and then show it else
    parentDiv.children('div').each(function() {
        if (this.id === hiddenID) {
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
    alert('deprecated');
    return false;
    var obj = $("#" + id + "LI");
    var ul = obj.closest('ul');
    var parentName = ul.get(0).id;
    parentName = parentName.replace(/\uFFFD/g, '');
    loadToolbarLi(id, parentName + "TabContent", reload);
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





/*
*
*
* NEW DESING FUNCTIONS
*
*/



function activateSidenav(id) {
    // deactivateActiveOne
    $('#' + id).parent().parent().children("div").each(function() {
        $(this).attr('class', 'mylist-group-item');
    });
    // activate tab
    $('#' + id).parent().attr('class', 'mylist-group-item active');
}

function loadSideNav(id, reload) {
    var contentID = "SideNavContent";

    activateSidenav(id);
    var url = $('#' + id).attr('src');
    var hiddenDivID = getHiddenDivID(id, contentID);
    if (reload) {
        loadContent(hiddenDivID, url);
    } else {
        //if div is empty load content
        if ($('#' + hiddenDivID).is(':empty')) {
            loadContent(hiddenDivID, url);
        } else {
            //show content
            $('#' + hiddenDivID).css("display", "block");
        }
    }
}

function findAndLoadActiveSideNav(id) {
    $('#' + id).children("div").each(function() {
        var item = $(this);
        var className = item.attr('class');
        if (className) {
            if (className.match(/active/i)) {
                tabid = $(this).children('div').attr('id');
                return loadSideNav(tabid, false);
            }
        }
    });
}

function loadNewSideNavTab(pk, id, url, reload, title) {
    // getTabID
    var tabID = id.replace("TabContent", "");
    // deactivate Tabs
    // deactivateActiveOne
    $('#' + tabID).children("div").each(function() {
        $(this).attr('class', 'mylist-group-item');
    });
    var keyValue = tabID+pk;
    // check if element exists
    if ($('#' + tabID + pk).length) {
        $('#' + tabID + pk).parent().attr('class', 'list-group-item active');
    } else {
        // createTab
        var tab = $("<div/>")
        .attr("class", 'list-group-item active');
        
        var link = $("<div/>")
        .attr("class", 'link')
        .attr("src", url)
        .attr("id", keyValue)
        .html(title);
        if (reload) {
            link.attr("onclick", 'loadSideNav(this.id, true)');
        } else {
            link.attr("onclick", 'loadSideNav(this.id, false)');
        }
        tab.append(link);

        var badge = $('<div/>')
        .attr("class", 'badge')
        .attr("onclick", 'closeSideNavTab(\'' + tabID + '\',\'' + tabID + pk + '\');')
        .html('x');
        tab.append(badge);
        var clean = $("<div/>")
        .attr("style", 'clear: both;');
        tab.append(clean);

        $("#" + tabID).append(tab);
    }
    // load Content
    loadSideNav(keyValue, false);
}

function closeSideNavTab(tabulatorID, tabToCloseID) {
    $('#' + tabToCloseID).parent().remove();
    var contentID = tabToCloseID+"Hidden";
    $('#' + contentID).remove();
    var opentab = $('#' + tabulatorID).children().first().children().first();
    var firstID = opentab.attr('id');
    var url = opentab.attr('src');
    loadSideNav(firstID, false);
}



/*
*
* Tabulator functions
*
*/

function activateTab(id) {
    // deactivateActiveOne
    $('#' + id + 'LI').parent().find("li").each(function() {
        $(this).attr('class', 'dropdown');
    });
    // activate tab
    $('#' + id + 'LI').attr('class', 'dropdown active');
}

function loadTab(id, reload) {
    var containerID = $('#'+id).parent().parent().attr('id');
    var contentID = containerID+"TabContent";

    activateTab(id);
    var url = $('#' + id).attr('src');
    var hiddenDivID = getHiddenDivID(id, contentID);
    if (reload) {
        loadContent(hiddenDivID, url);
    } else {
        //if div is empty load content
        if ($('#' + hiddenDivID).is(':empty')) {
            loadContent(hiddenDivID, url);
        } else {
            //show content
            $('#' + hiddenDivID).css("display", "block");
        }
    }
}

function findAndLoadActiveTab(id, reload=false) {
    $('#' + id).find("li").each(function() {
        var item = $(this);
        var className = item.attr('class');
        if (className) {
            if (className.match(/active/i)) {
                item.find("a").each(function() {
                    tabid = $(this).attr('id'); 
                    return loadTab(tabid, reload);
                });
            }
        }
    });
}
