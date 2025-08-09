--- @class cell
--- @field r number
--- @field c number

--- @class board
--- @field buf number
--- @field win number
--- @field width number
--- @field height number
--- @field bombs table<number>

local NUM_BOMBS = { [1] = 10, [2] = 40, [3] = 99 }
local WIDTH = { [1] = 9, [2] = 16, [3] = 30 }
local HEIGHT = { [1] = 9, [2] = 16, [3] = 16 }

--- @class board
local Board = {}

--- @param level number
--- @return board
function Board.new(level)
	local self = setmetatable({}, { __index = Board })
	self.buf = vim.api.nvim_create_buf(false, true)

	self.width = WIDTH[level] or 9
	self.height = HEIGHT[level] or 9
	local num_bombs = NUM_BOMBS[level] or 10

	local cells, lines = {}, {}
	for i = 0, self.height - 1 do
		local s = ""
		for j = 0, self.width - 1 do
			s = s .. "."
			vim.list_extend(cells, { self:cell_to_index(i, j) })
		end
		vim.list_extend(lines, { s })
	end

	vim.api.nvim_buf_set_lines(self.buf, 0, 1, true, lines)

	for i = 1, num_bombs do
		local j = math.random(i, #cells)
		cells[i], cells[j] = cells[j], cells[i]
	end

	self.bombs = vim.list_slice(cells, 1, num_bombs)

	local opts = {
		relative = "win",
		width = self.width,
		height = self.height,
		col = math.floor(vim.fn.winwidth(0) / 2) - math.floor(self.width / 2),
		row = math.floor(vim.fn.winheight(0) / 2) - math.floor(self.height / 2),
		style = "minimal",
		border = "bold",
	}
	self.win = vim.api.nvim_open_win(self.buf, true, opts)

	vim.api.nvim_set_option_value("winhl", "Normal:Normal", { win = self.win })
	vim.api.nvim_set_option_value("scrolloff", 0, { win = self.win })

	self:lock()

	return self
end

function Board:lock()
	vim.api.nvim_set_option_value("modifiable", false, { buf = self.buf })
end

function Board:unlock()
	vim.api.nvim_set_option_value("modifiable", true, { buf = self.buf })
end

--- @param r number
--- @param c number
--- @return number
function Board:cell_to_index(r, c)
	return r * self.width + c
end

--- @param i number
--- @return number, number
function Board:index_to_cell(i)
	return math.floor(i / self.width), math.fmod(i, self.width)
end

--- @param r number
--- @param c number
--- @param char string
function Board:set(r, c, char)
	vim.api.nvim_buf_set_text(self.buf, r, c, r, c + 1, { char })
end

--- @return number, number, string
function Board:get_pos()
	local pos = vim.api.nvim_win_get_cursor(self.win)
	local r = pos[1] - 1
	local c = pos[2]
	local char = vim.api.nvim_get_current_line():sub(c + 1, c + 1)
	return r, c, char
end

--- @param r number
--- @param c number
--- @return boolean
function Board:is_bomb(r, c)
	return vim.list_contains(self.bombs, self:cell_to_index(r, c))
end

--- @param r number
--- @param c number
--- @return number
function Board:get_num_surrounding_bombs(r, c)
	local n = 0
	for _, neighbor in ipairs({ { -1, -1 }, { -1, 0 }, { -1, 1 }, { 0, -1 }, { 0, 1 }, { 1, -1 }, { 1, 0 }, { 1, 1 } }) do
		local ri, ci = r + neighbor[1], c + neighbor[2]
		if
			ri >= 0
			and ri < self.height - 1
			and ci >= 0
			and ci < self.width
			and self:is_bomb(r + neighbor[1], c + neighbor[2])
		then
			n = n + 1
		end
	end
	return n
end

function Board:flag()
	self:unlock()
	local r, c, char = self:get_pos()
	print(r, c, char)
	local replace_with
	if char == "." then
		replace_with = "f"
	elseif char == "f" then
		replace_with = "."
	else
		replace_with = tostring(char)
	end
	self:set(r, c, replace_with)
	self:lock()
end

function Board:reveal()
	self:unlock()
	local r, c = self:get_pos()
	if self:is_bomb(r, c) then
		for _, i in ipairs(self.bombs) do
			local ri, ci = self:index_to_cell(i)
			print(i, ri, ci)
			self:set(ri, ci, "x")
		end
	else
		self:set(r, c, tostring(self:get_num_surrounding_bombs(r, c)))
	end
	self:lock()
end

vim.api.nvim_create_user_command("Minesweeper", function(opts)
	local b = Board.new(tonumber(opts.fargs[1]) or 3)

	vim.keymap.set("n", "<Space>f", function()
		b:flag()
	end, { buffer = b.buf })
	vim.keymap.set("n", "<Space>r", function()
		b:reveal()
	end, { buffer = b.buf })
end, { nargs = "?" })
