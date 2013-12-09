$.fn.scrollView = function() {
    return this.each(function() {
        $('html, body').animate({
            scrollTop : $(this).offset().top
        }, 1000);
    });
}

function getErrorMsg(resonseText) {
    resultText = '<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
    if (typeof (resonseText.status) !== 'undefined') {
        resultText += '<h4 class="alert-heading">Error: ' + resonseText.status
                + '</h4><p><div style="text-align:left">'
    } else {
        resultText += '<h4 class="alert-heading">Error occurred!</h4><p>'
    }

    if (typeof (resonseText.statusText) !== 'undefined') {
        resultText += resonseText.statusText;
    } else {
        resultText += resonseText;
    }
    resultText += '</div></p></div>';
    return resultText
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
    // setup some local variables
    form = $(formElement);
    // let's select and cache all the fields
    inputs = form.find("input, select, button, textarea");
    // serialize the data in the form
    serializedData = form.serialize();

    // magic to get the button value
    name = event.originalEvent.explicitOriginalTarget.name;
    if (name) {
        value = event.originalEvent.explicitOriginalTarget.value;
        serializedData += '&' + name + '=' + value;
    }

    // let's disable the inputs for the duration of the ajax request
    inputs.prop("disabled", true);

    // fire off the request
    request = $.ajax({
        url : uri,
        type : "post",
        data : serializedData,
     timeout: 3000 //3secs
    });

    // callback handler that will be called on success
    request.done(function(responseText, textStatus, XMLHttpRequest) {
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
            if (responseText.match(/^<!--PostError-->/gi)) {
                resultText = responseText;
            } else {
                resultText = getErrorMsg(responseText)
            }
            if (modalID) {
                $("#" + modalID + "body").html(resultText);
            } else {
                $("#" + refreshContainer + "").html(resultText);
            }
        }
    });

    // callback handler that will be called on failure
    request.fail(function(responseText, textStatus, XMLHttpRequest) {
        resultText = getErrorMsg(responseText)
        if (modalID) {
            $('#' + modalID + 'body').html(resultText);
        } else {

            $('#' + contentid + 'Errors').html(resultText);
        }
    });
    // callback handler that will be called regardless
    // if the request failed or succeeded
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
        hiddenDiv = contentid;
    } else {
        hiddenDiv = getHiddenDivID(contentid, contentid);
    }
    if ((hiddenDiv) && (url)) {
        $("#" + hiddenDiv).html(
                '<img src="/img/ajax-loader.gif" alt="loading"/> ');
        // load Content
        $.ajax({
                    url : url,
                     timeout: 3000, //3secs
                    success : function(response) {
                        if (response.match(/^(<HTML>)|(<html>)/)) {
                            $("#main").html(response);
                        } else {
                            $("#" + hiddenDiv).html(response);
                        }

                    },
                    error : function(response, type, message) {
                        $("#" + hiddenDiv)
                                .html(
                                        '<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button><h4 class="alert-heading">'
                                                + type
                                                + '</h4><p>'
                                                + message
                                                + '</p></div>');
                    }

                });
    }
}

function loadNewTab(pk, id, url, reload) {
    // getTabID
    tabID = id.replace("TabContent", "");
    // deactivate Tabs
    // deactivateActiveOne
    $('#' + tabID).find("li").each(function() {
        $(this).attr('class', '');
    });
    // check if element exists
    if ($('#' + tabID + pk + 'LI').length) {
        $('#' + tabID + pk + 'LI').attr('class', 'active');
    } else {
        // createTab
        var keyValue = tabID+pk
        var tab = $("<li/>")
        .attr("id", keyValue +'LI')
        .attr("class", 'active');
        var link = $('<a/>')
        .attr("href", '#')
        .attr("src", url)
        .attr("id", keyValue)
        .html("Event #" + pk);
        
        if (reload) {
            link.attr("onclick", 'loadTabLi(this.id, true)');
        } else {
            link.attr("onclick", 'loadTabLi(this.id, false)');
        }
        
        
        if (!reload) {
            var reload = $('<button/>')
            .attr("class", 'close')
            .attr("title", 'Reloads this Tab')
            .attr("type", 'button')
            .attr("onclick", 'loadTabLi("'+keyValue+'", true);')
            .html('&nbsp;&#x21bb;');
            link.append(reload);
            
        }
        
        
        var button = $('<button/>')
        .attr("class", 'close')
        .attr("title", 'Remove this Tab')
        .attr("type", 'button')
        .attr("onclick", 'closeTab(\'' + tabID + '\',\'' + tabID + pk + 'LI\');')
        .html('&nbsp;&times;');
        link.append(button);
        tab.append(link);
        
        $("#" + tabID).append(tab);
    }
    // load Content
    loadContent(id, url);
}

function loadTabFromPaginator(pk, id, url, tabid) {
    // Not done yet
    // TODO: jojo do ass nach fill
    loadTab(url, tabid);
}

function closeTab(tabulatorID, tabToCloseID) {

    $('#' + tabToCloseID).find("a").each(function() {
        // normalerweis get et just een
        $(this).attr('onclick', '').unbind('click');
    });

    $('#' + tabToCloseID).remove();

    // goback to first tab
    $('#' + tabulatorID).find("a").each(function() {
        // loadfirst tab
        url = $(this).attr('src');
        loadTab(url, this.id);
        return false;
    });
}

function activateLi(id) {
    // deactivateActiveOne
    $('#' + id + 'LI').parent().find("li").each(function() {
        $(this).attr('class', '');
    });
    // activate tab
    $('#' + id + 'LI').attr('class', 'active');
}

function loadTab(url, id) {
    activateLi(id);
    parentName = $('#' + id + 'LI').parent().attr('id');
    loadContent(parentName + 'TabContent', url);
}

function findAndLoadActiveLi(id, contentID) {
    $('#' + id).find("li").each(function() {
        var className = $(this).attr('class');
        if (className == 'active') {
            $(this).find("a").each(function() {
                url = $(this).attr('src');
                loadContent(contentID, url);
            });
        }
    })
}

function hideHidden(contentID) {
    $('#' + contentID).children('div').each(function() {
        if (this.id.match(/Hidden$/)) {
            $(this).css("display", "none");
        }
    });
}

function getHiddenDivID(id, contentID) {
    var found = false;
    //hide all in container
    hideHidden(contentID);
    var hiddenID =   id + 'Hidden';
    var parentDiv = $('#' + contentID);
    parentParend = parentDiv.parent();
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
    url = $('#' + id).attr('src');
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
    obj = $("#" + id + "LI");
    ul = obj.closest('ul');
    parentName = ul.get(0).id;
    parentName = parentName.replace(/\uFFFD/g, '');
    loadToolbarLi(id, parentName + "TabContent", reload);
}

function showPaginatorModal(id, title, contentUrl, postUrl, refresh,
        refreshContentID, refreshContentUrl) {
    $('#' + id).modal('show');
    loadContent('' + id + 'body', contentUrl);
    $('#' + id + 'Label').html(title);
    if (postUrl) {
        $("#" + id + "Form").unbind('submit');
        $("#" + id + "Form").submit(function(event) {

            // setup some local variables
            form = $('#' + id + 'Form');
            // let's select and cache all the fields
            inputs = form.find("input, select, button, textarea");
            // serialize the data in the form
            serializedData = form.serialize();

            // magic to get the button value
            name = event.originalEvent.explicitOriginalTarget.name;
            if (name) {
                value = event.originalEvent.explicitOriginalTarget.value;
                serializedData += '&' + name + '=' + value;
            }

            // let's disable the inputs for the duration of the ajax request
            inputs.prop("disabled", true);

            // fire off the request
            request = $.ajax({
                url : postUrl,
                type : "post",
                data : serializedData
            });

            // callback handler that will be called on success
            request.done(function(responseText, textStatus, XMLHttpRequest) {
                if (responseText.match(/^<!--OK--/gi)) {
                    $('#' + id).modal("hide");
                    // refrehshPage & container if needed
                    if (refresh) {
                        loadContent(refreshContentID, refreshContentUrl);
                    }
                    // workaround---
                    $('.modal-backdrop').remove();
                    document.documentElement.style.overflow = "auto";
                    document.body.style.marginRight = '0px';
                } else {
                    if (responseText.match(/^<!--PostError-->/gi)) {
                        resultText = responseText;
                    } else {
                        resultText = getErrorMsg(responseText)
                    }
                    $("#'+id+'body").html(resultText);
                }
            });

            // callback handler that will be called on failure
            request.fail(function(responseText, textStatus, XMLHttpRequest) {
                resultText = getErrorMsg(responseText)
                $("#" + id + "body").html(resultText);
            });
            // callback handler that will be called regardless
            // if the request failed or succeeded
            request.always(function() {
                // reenable the inputs
                inputs.prop("disabled", false);
            });
            // prevent default posting of form
            event.preventDefault();
        });
        $('#' + id + 'Footer')
                .html(
                        '<input class="btn btn-primary" value="'
                                + 'Save changes" type="submit"><button class="btn btn-default" data-'
                                + 'dismiss="modal">Close</button>');
    } else {
        $('#' + id + 'Footer').html(
                '<button class="btn btn-default" data-dismiss="'
                        + 'modal">Close</button>');
    }
}

function genericDialogCall(url, refreshContainer, refreshUrl, refreshContent,
        doCloseTab, tabID, tabToClose) {
    $.ajax({
        url : url,
        error : function(response) {
            if (response.match(/^(<HTML>)|(<html>)/)) {
                $("#main").html(response);
            } else {
                alert(response.responseText);
            }
        },
        success : function(response) {
            if (response.match(/^(<HTML>)|(<html>)/)) {
                $("#main").html(response);
            } else {
                if (response.match(/^<!--OK--/gi)) {
                    // do refresh
                    if (refreshContent) {
                        loadContent(refreshContainer, refreshUrl);
                    } else {
                        if (doCloseTab) {
                            closeTab(tabID, tabToClose);
                        }
                    }
                } else {
                    alert('An error occured:\n' + response);
                }
            }
        },
     timeout: 3000 //3secs
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
