-- phpMyAdmin SQL Dump
-- version 3.4.9
-- http://www.phpmyadmin.net
--
-- ホスト: localhost
-- 生成時間: 2012 年 3 月 08 日 01:12
-- サーバのバージョン: 5.5.21
-- PHP のバージョン: 5.3.10

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- データベース: `vulpix`
--

-- --------------------------------------------------------

--
-- テーブルの構造 `auth`
--

CREATE TABLE IF NOT EXISTS `auth` (
  `member_id` int(11) NOT NULL,
  `secret` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  KEY `member_id` (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `contest`
--

CREATE TABLE IF NOT EXISTS `contest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text NOT NULL,
  `description` mediumtext NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `invisible` int(11) NOT NULL,
  `create` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

--
-- テーブルの構造 `contest_problem`
--

CREATE TABLE IF NOT EXISTS `contest_problem` (
  `contest_id` int(11) NOT NULL,
  `problem_id` int(11) NOT NULL,
  KEY `contest_id` (`contest_id`),
  KEY `problem_id` (`problem_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `contest_submit`
--

CREATE TABLE IF NOT EXISTS `contest_submit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contest_id` int(11) NOT NULL,
  `problem_id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `testpoint` text NOT NULL,
  `score` int(11) NOT NULL,
  `costtime` int(11) NOT NULL,
  `costmemory` int(11) NOT NULL,
  `lang` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `msg` mediumtext NOT NULL,
  `user_agent` text NOT NULL,
  `ip` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `contest_id` (`contest_id`),
  KEY `problem_id` (`problem_id`),
  KEY `member_id` (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- テーブルの構造 `member`
--

CREATE TABLE IF NOT EXISTS `member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(200) NOT NULL,
  `username_lower` varchar(200) NOT NULL,
  `password` varchar(200) NOT NULL,
  `email` text NOT NULL,
  `website` text NOT NULL,
  `tagline` text NOT NULL,
  `bio` mediumtext NOT NULL,
  `gravatar_link` text NOT NULL,
  `create` datetime NOT NULL,
  `admin` int(11) NOT NULL,
  `lang` int(11) NOT NULL COMMENT 'pascal - 1, c - 2, cpp - 3',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

-- --------------------------------------------------------

--
-- テーブルの構造 `node`
--

CREATE TABLE IF NOT EXISTS `node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `description` text NOT NULL,
  `link` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- テーブルの構造 `note`
--

CREATE TABLE IF NOT EXISTS `note` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text NOT NULL,
  `content` mediumtext NOT NULL,
  `member_id` int(11) NOT NULL,
  `create` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `member_id` (`member_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=10 ;

-- --------------------------------------------------------

--
-- テーブルの構造 `problem`
--

CREATE TABLE IF NOT EXISTS `problem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text NOT NULL,
  `shortname` varchar(200) NOT NULL,
  `content` mediumtext NOT NULL,
  `timelimit` int(11) NOT NULL,
  `memlimit` int(11) NOT NULL,
  `testpoint` int(11) NOT NULL,
  `invisible` int(11) NOT NULL,
  `create` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- テーブルの構造 `problem_tag`
--

CREATE TABLE IF NOT EXISTS `problem_tag` (
  `problem_id` int(11) NOT NULL,
  `tagname` text NOT NULL,
  KEY `problem_id` (`problem_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `related_problem`
--

CREATE TABLE IF NOT EXISTS `related_problem` (
  `problem_id` int(11) NOT NULL,
  `note_id` int(11) NOT NULL,
  KEY `problem_id` (`problem_id`),
  KEY `note_id` (`note_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `reply`
--

CREATE TABLE IF NOT EXISTS `reply` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` mediumtext NOT NULL,
  `member_id` int(11) NOT NULL,
  `topic_id` int(11) NOT NULL,
  `create` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `topic_id` (`topic_id`),
  KEY `member_id` (`member_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- テーブルの構造 `reset_mail`
--

CREATE TABLE IF NOT EXISTS `reset_mail` (
  `member_id` int(11) NOT NULL,
  `secret` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  KEY `member_id` (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `submit`
--

CREATE TABLE IF NOT EXISTS `submit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `problem_id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `testpoint` text NOT NULL,
  `score` int(11) NOT NULL,
  `costtime` int(11) NOT NULL,
  `costmemory` int(11) NOT NULL,
  `timestamp` text NOT NULL,
  `lang` int(11) NOT NULL,
  `user_agent` text NOT NULL,
  `ip` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `problem_id` (`problem_id`),
  KEY `member_id` (`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- テーブルの構造 `topic`
--

CREATE TABLE IF NOT EXISTS `topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text NOT NULL,
  `content` mediumtext NOT NULL,
  `node_id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `create` datetime NOT NULL,
  `last_reply` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `node_id` (`node_id`),
  KEY `member_id` (`member_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

--
-- ダンプしたテーブルの制約
--

--
-- テーブルの制約 `auth`
--
ALTER TABLE `auth`
  ADD CONSTRAINT `auth_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);

--
-- テーブルの制約 `contest_problem`
--
ALTER TABLE `contest_problem`
  ADD CONSTRAINT `contest_problem_ibfk_1` FOREIGN KEY (`contest_id`) REFERENCES `contest` (`id`),
  ADD CONSTRAINT `contest_problem_ibfk_2` FOREIGN KEY (`problem_id`) REFERENCES `problem` (`id`);

--
-- テーブルの制約 `contest_submit`
--
ALTER TABLE `contest_submit`
  ADD CONSTRAINT `contest_submit_ibfk_1` FOREIGN KEY (`contest_id`) REFERENCES `contest` (`id`),
  ADD CONSTRAINT `contest_submit_ibfk_2` FOREIGN KEY (`problem_id`) REFERENCES `problem` (`id`),
  ADD CONSTRAINT `contest_submit_ibfk_3` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);

--
-- テーブルの制約 `note`
--
ALTER TABLE `note`
  ADD CONSTRAINT `note_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);

--
-- テーブルの制約 `problem_tag`
--
ALTER TABLE `problem_tag`
  ADD CONSTRAINT `problem_tag_ibfk_1` FOREIGN KEY (`problem_id`) REFERENCES `problem` (`id`);

--
-- テーブルの制約 `related_problem`
--
ALTER TABLE `related_problem`
  ADD CONSTRAINT `related_problem_ibfk_1` FOREIGN KEY (`problem_id`) REFERENCES `problem` (`id`),
  ADD CONSTRAINT `related_problem_ibfk_2` FOREIGN KEY (`note_id`) REFERENCES `note` (`id`);

--
-- テーブルの制約 `reply`
--
ALTER TABLE `reply`
  ADD CONSTRAINT `reply_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`),
  ADD CONSTRAINT `reply_ibfk_2` FOREIGN KEY (`topic_id`) REFERENCES `topic` (`id`);

--
-- テーブルの制約 `reset_mail`
--
ALTER TABLE `reset_mail`
  ADD CONSTRAINT `reset_mail_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);

--
-- テーブルの制約 `submit`
--
ALTER TABLE `submit`
  ADD CONSTRAINT `submit_ibfk_1` FOREIGN KEY (`problem_id`) REFERENCES `problem` (`id`),
  ADD CONSTRAINT `submit_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);

--
-- テーブルの制約 `topic`
--
ALTER TABLE `topic`
  ADD CONSTRAINT `topic_ibfk_1` FOREIGN KEY (`node_id`) REFERENCES `node` (`id`),
  ADD CONSTRAINT `topic_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);

