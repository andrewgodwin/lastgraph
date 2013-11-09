
window.lastgraph = {
	
	displayMessage: function (msg) {
		$("#stats").html(msg);
	},
	
	getMessage: function (msg) {
		return $("#stats").html();
	},
	
	updateQueue: function () {
		$.getJSON("/ajax/" + lastgraph.username + "/queuepos/", function (pos) {
			if (pos === null) {
				lastgraph.checkUsername(true);
			} else {
				lastgraph.drawQueue(pos);
				lastgraph.updateTimeout = setTimeout(lastgraph.updateQueue, 15000);
			}
		});
	},
	
	drawQueue: function (pos) {
		lastgraph.displayMessage("<em>Fetching</em> your data; you're in queue position <em>" + pos + "</em>");
	},
	
	checkUsername: function (skipChanges) {
		if (!skipChanges) {
			lastgraph.displayMessage("<em>Hold on</em> while we <em>check</em> that username...");
		}
		lastgraph.showLoading();
		lastgraph.username = $("#id_username").val();
		$.getJSON("/ajax/" + lastgraph.username + "/ready/", function (ok) {
			if (!!ok) {
				lastgraph.initUser(ok);
			} else if (ok === 0) {
				lastgraph.hideLoading();
				lastgraph.displayMessage("That username has no <em>played tracks</em>.");
			} else if (ok === false) {
				lastgraph.showLoading("Fetching...");
				if (!!lastgraph.updateTimeout) {
					clearTimeout(lastgraph.updateTimeout);
				}
				lastgraph.updateQueue();
			} else {
				lastgraph.hideLoading();
				lastgraph.displayMessage("That doesn't seem to be a <em>last.fm</em> username.");
			}
		});
	},
	
	initUser: function (numWeeks) { // We have a valid, up to date username - now go!
		// Jump to their user page
		document.location.href = "/user/" + lastgraph.username + "/";
	},
	
	showLoading: function (text) {
		if (!text) { text = "Loading..."; }
		$("#loading_text").html(text);
		$("#loading").animate({right: 0}, 500);
	},
	
	hideLoading: function () {
		$("#loading").animate({right: -110}, 500);
	},
	
	resizeGraphs: function () {
		// Hook up graphed H1s
		$("h1.graphed").each(function () {
			var self = $(this);
			this.style.backgroundImage = "url(/graph/"+lastgraph.username+"/timeline-basic/"+self.innerWidth()+"/"+self.innerHeight()+"/)";
		})
		// Resize resizeable graphs
		$("img.resizeable_graph").each(function () {
			var self = $(this);
			if (!this.base_src) this.base_src = this.src;
			this.src = this.base_src + self.parent().innerWidth() + "/" + 300 /*self.parent().innerHeight()*/ + "/";
		})
	}
	
}

$(function () {
	
	// Make the username box have a default content,
	// and hook up its enter functions
	$("#id_username").focus(function (e) {
		// On focus: clear the box and change the msg if we're 'empty'
		if (this.defaulted) {
			this.value = "";
			lastgraph.displayMessage("When you're ready, hit <em>return</em>.");
			this.defaulted = false;
			$(this).removeClass("default");
		}
	}).
	blur(function (e) {
		// On blur: if empty, display a default value, etc.
		if (!this.default_value) {
			this.default_value = this.value;
			this.default_message = lastgraph.getMessage();
			this.value = "";
		}
		if (!this.value) {
			this.value = this.default_value;
			lastgraph.displayMessage(this.default_message);
			this.defaulted = true;
			$(this).addClass("default");
		}
	}).
	blur(). // We start off empty, so fill in default
	keydown(function (e) {
		// If they pressed enter, we want to fetch their status
		if(e.keyCode == 13) {
			lastgraph.checkUsername();
		}
	});
	
	// Change DateInput to use YYYY/MM/DD (thanks Jon)
	$.extend(DateInput.DEFAULT_OPTS, {
		stringToDate: function(string) {
			var matches;
			if (matches = string.match(/^(\d{4,4})\/(\d{2,2})\/(\d{2,2})$/)) {
			return new Date(matches[1], matches[2] - 1, matches[3]);
			} else {
			return null;
			};
		},
		
		dateToString: function(date) {
			var month = (date.getMonth() + 1).toString();
			var dom = date.getDate().toString();
			if (month.length == 1) month = "0" + month;
			if (dom.length == 1) dom = "0" + dom;
			return date.getFullYear() + "/" + month + "/" + dom;
		}
	});
	
	lastgraph.resizeGraphs();
	$(window).bind("resize", lastgraph.resizeGraphs);
	
	$("#id_start, #id_end").date_input();
	
});

