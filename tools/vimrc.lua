local augroup = vim.api.nvim_create_augroup("ralismark.github.io", { clear = true })

local function try_require(m)
	local ok, m = pcall(require, m)
	if ok then return m else return nil end
end

local ls = try_require("luasnip")
if ls then
	-- Luasnip abbreviations
	local s = ls.snippet
	local sn = ls.snippet_node
	local isn = ls.indent_snippet_node
	local t = ls.text_node
	local i = ls.insert_node
	local f = ls.function_node
	local c = ls.choice_node
	local d = ls.dynamic_node
	local r = ls.restore_node
	local events = require("luasnip.util.events")
	local ai = require("luasnip.nodes.absolute_indexer")
	local fmt = require("luasnip.extras.fmt").fmt
	local m = require("luasnip.extras").m
	local lambda = require("luasnip.extras").l
	local rep = require("luasnip.extras").rep

	local show_condition = function(before)
		return before:match("^%s*%.%.")
	end

	-- snippets
	ls.add_snippets("pandoc", {
		s({
			trig = ".. details::",
			show_condition = show_condition,
		}, {
			t({ ".. details:: " }), i(1), t({ "",
				"",
				"\t", }), i(0),
		}),
		s({
			trig = ".. figure::",
			show_condition = show_condition,
		}, {
			t({ ".. figure:: " }), i(1), t({ "",
				"\t:alt: ", }), i(2), t({ "",
				"",
				"\t", }), i(0),
		}),
	})

	local function skeleton(pat, snip)
		vim.api.nvim_create_autocmd("BufNewFile", {
			group = augroup,
			pattern = pat,
			callback = function(au)
				if vim.b.skeleton == nil then
					vim.b.skeleton = true

					ls.snip_expand(snip, {})
				end
			end,
		})
	end

	skeleton("*/ralismark.github.io/*.md", s("", {
		t({ "---",
			"layout: post",
			"title: ", }), i(1), t({ "",
			"excerpt:",
			"date: " }), f(function() return vim.fn.strftime("%Y-%m-%d") end), t({ "",
			"tags:",
			"---",
			"",
			"" })
	}))
	skeleton("*/ralismark.github.io/*/links/*.md", s("", {
		t({ "---",
			"layout: link",
			"title: ", }), i(1), t({ "",
			"url: ", }), i(2), t({ "",
			"date: " }), f(function() return vim.fn.strftime("%Y-%m-%d") end), t({ "",
			"tags:",
			"---",
			"",
			"" })
	}))
end

vim.filetype.add {
	extension = {
		md = "markdown.django",
		html = "htmldjango",
	}
}
