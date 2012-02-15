-- phpMyAdmin SQL Dump
-- version 3.3.2deb1ubuntu1
-- http://www.phpmyadmin.net
--
-- ホスト: localhost
-- 生成時間: 2012 年 2 月 15 日 20:59
-- サーバのバージョン: 5.1.41
-- PHP のバージョン: 5.3.2-1ubuntu4.13

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- データベース: `vulpix`
--

-- --------------------------------------------------------

--
-- テーブルの構造 `auth`
--

CREATE TABLE IF NOT EXISTS `auth` (
  `uid` int(11) NOT NULL,
  `secret` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `member`
--

CREATE TABLE IF NOT EXISTS `member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(200) NOT NULL,
  `username_lower` varchar(200) NOT NULL,
  `password` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `gravatar_link` text NOT NULL,
  `create` datetime NOT NULL,
  `website` varchar(200) DEFAULT NULL,
  `tagline` text,
  `bio` mediumtext,
  `admin` tinyint(1) NOT NULL DEFAULT '0',
  `lang` int(11) NOT NULL DEFAULT '1' COMMENT '1 - pas 2 - c 3 - c++',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `node`
--

CREATE TABLE IF NOT EXISTS `node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `description` text NOT NULL,
  `link` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

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
  `link_problem` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `problem`
--

CREATE TABLE IF NOT EXISTS `problem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text NOT NULL,
  `shortname` text NOT NULL,
  `content` mediumtext NOT NULL,
  `content_html` mediumtext NOT NULL,
  `inputfmt` text NOT NULL,
  `outputfmt` text NOT NULL,
  `samplein` text NOT NULL,
  `sampleout` text NOT NULL,
  `timelimit` int(11) NOT NULL DEFAULT '1000' COMMENT 'ms',
  `memlimit` int(11) NOT NULL DEFAULT '128' COMMENT 'mb',
  `tags` mediumtext,
  `create` datetime NOT NULL,
  PRIMARY KEY (`id`)
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- テーブルの構造 `reset_mail`
--

CREATE TABLE IF NOT EXISTS `reset_mail` (
  `uid` int(11) NOT NULL,
  `secret` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

--
-- ダンプしたテーブルの制約
--

--
-- テーブルの制約 `auth`
--
ALTER TABLE `auth`
  ADD CONSTRAINT `auth_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `member` (`id`);

--
-- テーブルの制約 `reset_mail`
--
ALTER TABLE `reset_mail`
  ADD CONSTRAINT `reset_mail_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `member` (`id`);

